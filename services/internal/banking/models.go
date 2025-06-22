package banking


type BankAccount struct {
	// IDs are generated manually upon loading users
	ID uint64 `gorm:"primaryKey"`
}

type Product2BankAccount struct {
	BankAccountID BankAccount `gorm:"foreignKey:ID"`
	ProductID Product `gorm:"foreignKey:ID"`
	Count uint64
}
