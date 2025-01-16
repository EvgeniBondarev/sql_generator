SELECT
    c.Id AS CategoryId,
    c.Name AS CategoryName,
    p.Id AS ProductId,
    p.Article AS ProductArticle,
    p.Brand AS ProductBrand,
    a.Id AS AttributeId,
    a.AttributeName,
    a.AttributeValue
FROM
    Categories c
LEFT JOIN
    Products p ON c.Id = p.CategoryId
LEFT JOIN
    Attributes a ON p.Id = a.ProductId
ORDER BY
    c.Id, p.Id, a.Id;



SET SQL_SAFE_UPDATES = 0;

delete from Categories;
delete from Products;
delete from Attributes;

SET SQL_SAFE_UPDATES = 1;



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

