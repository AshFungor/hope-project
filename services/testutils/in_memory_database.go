package testutils

import (
	"fmt"
	"strings"
	"testing"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func WithInMemoryDatabase(t *testing.T, config *gorm.Config, models ...any) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), config)
	if err != nil {
		t.Fatalf("failed to create in-memory database: %v", err)
	}

	if err := db.AutoMigrate(models...); err != nil {
		t.Fatalf("migration failed: %v", err)
	}

	return db
}

func DumpSchema(t *testing.T, ctx *gorm.DB) string {
	var out strings.Builder
	if ctx.Dialector.Name() != "sqlite" {
		t.Fatalf("failed to get database schema: only sqlite is supported for testing purposes")
	}

	var tables []string
	if err := ctx.Raw(`SELECT name FROM sqlite_master WHERE type='table'`).Scan(&tables).Error; err != nil {
		t.Fatalf("failed to list tables: %v", err)
	}

	for _, table := range tables {
		out.WriteString(fmt.Sprintf("table: %v\n", table))

		rows, err := ctx.Raw(fmt.Sprintf(`PRAGMA table_info(%v)`, table)).Rows()
		if err != nil {
			t.Fatal(err)
		}
		defer rows.Close()

		for rows.Next() {
			var cid int
			var name, typ string
			var notnull, pk int
			var dflt any

			if err = rows.Scan(&cid, &name, &typ, &notnull, &dflt, &pk); err != nil {
				t.Fatalf("failed to acquire column info: %v", err)
			}

			out.WriteString(
				fmt.Sprintf(
					"- column #%d: name=%s, type=%s, notnull=%v, default=%v, primary_key=%v\n", 
					cid, name, typ, notnull != 0, dflt, pk != 0,
				),
			)
		}
	}

	return out.String()
}