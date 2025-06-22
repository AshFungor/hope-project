package banking

import (
	"fmt"
	"time"

	"gorm.io/gorm"
)

type Product struct {
	ID uint64 `gorm:"primaryKey"`
	Category string
	Name string
	Level uint
}

type Consumption struct {
	ID uint64 `gorm:"primaryKey"`
	BankAccountID uint64
	BankAccount BankAccount `gorm:"foreignKey:ID"`
	ProductID uint64
	Product Product `gorm:"foreignKey:ID"`
	Count uint64
	ConsumedAt int64 `gorm:"autoCreateTime"` // in unix seconds
}

type VerboseConsumption struct {
	Name string
	Count uint64
	ConsumedAt int64
}

type ConsumptionSummary struct {
	Category string
	BankAccountID uint64
	Records []VerboseConsumption
}

func (this *Product) String() string {
	return fmt.Sprintf(
		"Product[ID=%v, Category=%v, Name=%v, Level=%v]",
		this.ID, this.Category, this.Name, this.Level,
	)
}

func (this *Consumption) String() string {
	return fmt.Sprintf(
		"Consumption[ID=%v, BankAccountID=%v, ProductID=%v, Count=%v, ConsumedAt=%v]",
		this.ID, this.BankAccountID, this.ProductID, this.Count, this.ConsumedAt,
	)
}

func (this *VerboseConsumption) String() string {
	return fmt.Sprintf(
		"VerboseConsumption[Name=%v, Count=%v, ConsumedAt=%v]",
		this.Name, this.Count, this.ConsumedAt, 
	)
}

func GetRecentConsumptions(ctx *gorm.DB, bankAccountID uint64, category string, span time.Duration) (*ConsumptionSummary, error) {
	var products []Product
	query := ctx.Model(&Product{}).
		Select("id", "name", "level").
		Where("category = ?", category).
		Find(&products)
	if err := query.Error; err != nil {
		return nil, err
	}

	productIDs := make([]uint64, len(products))
	for i, product := range products {
		productIDs[i] = product.ID
	}

	var (
		now = time.Now().Unix()
		since = now - int64(span.Seconds())
	)

	var records []VerboseConsumption
	query = ctx.
		Model(&Consumption{}).
		Select(
			"consumptions.count",
			"consumptions.consumed_at",
			"products.name",
		).
		Joins("LEFT JOIN products ON consumptions.product_id = products.id").
		Where(
			"consumptions.bank_account_id = ? AND consumptions.product_id IN ? AND consumptions.consumed_at > ? AND consumptions.consumed_at <= ?",
			bankAccountID, productIDs, since, now,
		).
		Scan(&records)

	if err := query.Error; err != nil {
		return nil, err
	}

	summary := ConsumptionSummary{
		Category: category,
		BankAccountID: bankAccountID,
		Records: records,
	}

	return &summary, nil
}
