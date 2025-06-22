package config

import (
	"os"
	"strings"
	"testing"
)

var (
	minimalJsonConfig string = `
	{
		"port": 8000,
		"postgres": {
			"user": "user",
			"password": "password",
			"uri": "postgres://user:password@localhost:5432/db"
		}
	}`
	fullJsonConfig string = `
	{
		"logging": {
			"stdout": {
				"enabled": true,
				"stderr": true,
				"stdout": true
			},
			"file": {
				"enabled": true,
				"filename": "log.txt",
				"size_threshold": 1048576
			}
		},
		"port": 8000,
		"postgres": {
			"user": "user",
			"password": "password",
			"uri": "postgres://user:password@localhost:5432/db"
		}
	}`
)

func TestLoads(t *testing.T) {
	reader := strings.NewReader(minimalJsonConfig)
	var appConfig AppConfig
	if err := appConfig.LoadFrom(reader); err != nil {
		t.Fatalf("failed to load less: %v", err)
	}

	reader.Reset(fullJsonConfig)
	if err := appConfig.LoadFrom(reader); err != nil {
		t.Fatalf("failed to load more: %v", err)
	}
}

func TestLoadsFromFile(t *testing.T) {
	tmpFile, err := os.CreateTemp(t.TempDir(), "config-*.json")
	if err != nil {
		t.Fatalf("failed to create temp file: %v", err)
	}

	defer tmpFile.Close()
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.Write([]byte(fullJsonConfig)); err != nil {
		t.Fatalf("failed to write to temp config file: %v", err)
	}

	var cfg AppConfig
	if err := cfg.LoadFromFile(tmpFile.Name()); err != nil {
		t.Fatalf("failed to load from file: %v", err)
	}
}
