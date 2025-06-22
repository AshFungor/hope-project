package config

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
)

type AppConfig struct {
	AppPort uint32 `json:"port"`

	Logging	*struct {
		Stdout *struct {
			Enabled	bool `json:"enabled"`
			Stderr bool `json:"stderr"`
			Stdout bool `json:"stdout"`
		} `json:"stdout"`
		
		File *struct {
			Enabled	bool `json:"enabled"`
			Filename string `json:"filename"`
			SizeThreshold uint64 `json:"size_threshold"`
		} `json:"file"`

	} `json:"logging"`

	Postgres struct {
		User string `json:"user"`
		Password string `json:"password"`
		URI string `json:"uri"`

	} `json:"postgres"`
}

func (this *AppConfig) LoadFrom(reader io.Reader) error {
	decoder := json.NewDecoder(reader)
	decoder.DisallowUnknownFields()

	if err := decoder.Decode(this); err != nil {
		return fmt.Errorf("could not decode app configuration: %w", err)
	}
	
	return nil
}

func (this *AppConfig) LoadFromFile(path string) error {
	fd, err := os.Open(path);
	if err != nil {
		return fmt.Errorf("could not open app configuration file: %w", err)
	}
	defer fd.Close()

	return this.LoadFrom(fd)
}
