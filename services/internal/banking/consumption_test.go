package banking

import (
	"log"
	"testing"
	"time"

	"github.com/AshFungor/hope-project/testutils"
	"github.com/stretchr/testify/assert"
	"gorm.io/gorm"
)

func TestRelevantConsumptions(t *testing.T) {
	ctx := testutils.WithInMemoryDatabase(t, &gorm.Config{}, Product{}, Consumption{}, BankAccount{})
	log.Print(testutils.DumpSchema(t, ctx))

	products := []Product{
		{Category: "food", Name: "Apple", Level: 1},
		{Category: "food", Name: "Banana", Level: 2},
		{Category: "drink", Name: "Water", Level: 1},
	}

	now := time.Now().Unix()
	consumptions := []Consumption{
		{
			BankAccountID: 1,
			BankAccount: BankAccount{ID: 1},
			ProductID: 0,
			Product: products[0],
			Count: 2,
			ConsumedAt: now - 60,
		},
		{
			BankAccountID: 1,
			BankAccount: BankAccount{ID: 1},
			ProductID: 1,
			Product: products[1],
			Count: 1,
			ConsumedAt: now - 180,
		},
		{
			BankAccountID: 1,
			BankAccount: BankAccount{ID: 2},
			ProductID: 2,
			Product: products[2],
			Count: 5,
			ConsumedAt: now - 30,
		},
	}

	err := ctx.Transaction(func(tx *gorm.DB) error {
		if err := tx.Create(&products).Error; err != nil {
			return err
		}
		if err := tx.Create(&consumptions).Error; err != nil {
			return err
		}
		return nil
	})
	if err != nil {
		t.Fatalf("query: failed to add test data into database: %v", err)
	}

	span := time.Second * 120
	summary, err := GetRecentConsumptions(ctx, 1, "food", span)
	if err != nil {
		t.Fatalf("query: failed to acquire summary: %v", err)
	}

	assert := assert.New(t)
	assert.Equal(1, len(summary.Records))

	log.Printf("summary: now (caller's context): %v", now)
	for _, record := range summary.Records {
		log.Printf("summary: picked up record: %v", record.String())
		assert.Less(now - int64(span.Seconds()), record.ConsumedAt)
	}
}
