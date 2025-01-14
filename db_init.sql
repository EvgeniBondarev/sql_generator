CREATE TABLE Categories (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL UNIQUE -- Название категории (например, "Колодки тормозные")
);

CREATE TABLE Products (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Article VARCHAR(50) NOT NULL, -- Артикул
    Brand VARCHAR(50) NOT NULL, -- Бренд
    CategoryId INT, -- Ссылка на категорию
    FOREIGN KEY (CategoryId) REFERENCES Categories(Id) ON DELETE SET NULL
);

CREATE TABLE Attributes (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    ProductId INT NOT NULL, -- Ссылка на товар в Products
    AttributeName VARCHAR(50) NOT NULL, -- Название атрибута (например, "Место_установки", "Транспортные_средства")
    AttributeValue TEXT, -- Значение атрибута (например, "передние", "CAMRY")
    FOREIGN KEY (ProductId) REFERENCES Products(Id) ON DELETE CASCADE
);