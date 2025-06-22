package main

import (
	"fmt"

	"github.com/AshFungor/hope-project/internal/banking"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// func loadTemplates() *template.Template {
// 	tmpl := template.New("")
// 	err := filepath.Walk("internal/banking/templates", func(path string, info fs.FileInfo, err error) error {
// 		if filepath.Ext(path) == ".html" {
// 			_, err = tmpl.ParseFiles(path)
// 		}
// 		return err
// 	})
// 	if err != nil {
// 		log.Fatalf("template load error: %v", err)
// 	}
// 	return tmpl
// }

func main() {
	// r := gin.Default()
	// r.SetHTMLTemplate(loadTemplates())

	// r.GET("/", func(c *gin.Context) {
	// 	c.HTML(http.StatusOK, "home.html", gin.H{
	// 		"title": "Money UI",
	// 		"balance": 42.50,
	// 	})
	// })

	// r.Run(":8080")

	dsn := "host=database user=hope password=somepasswd dbname=hope port=5432"
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})

	if err != nil {
		fmt.Println("error")
	}

	product := banking.Product{Category: "currency", Name: "money", Level: 1}
	db.Create(&product)

	fmt.Printf("%v", product)
}
