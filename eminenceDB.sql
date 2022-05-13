CREATE TABLE `userData` (
	`phoneNumber` VARCHAR(20) NOT NULL,
	`firstName` VARCHAR(100),
	`lastName` VARCHAR(100),
	`emailID` VARCHAR(100),
	`customerType` VARCHAR(100),
	`shippingAddress` VARCHAR(500),
	`billingAddress` VARCHAR(500),
    `sellingPriceWithGST` FLOAT,
	`GSTIN` VARCHAR(100) DEFAULT 'N/A',
	PRIMARY KEY (`phoneNumber`)
) ENGINE=InnoDB;

CREATE TABLE `pricingModel` (
	`category` VARCHAR(200) NOT NULL,
	`sellingPrice` FLOAT NOT NULL,
	`minOrderQuantity` BIGINT(100) NOT NULL
) ENGINE=InnoDB;

INSERT INTO `pricingModel` (category, sellingPrice, minOrderQuantity) VALUES ("Manufacturer", 60, 1200);
INSERT INTO `pricingModel` (category, sellingPrice, minOrderQuantity) VALUES ("Distributor/Wholeseller", 70, 600);
INSERT INTO `pricingModel` (category, sellingPrice, minOrderQuantity) VALUES ("Retailer", 100, 50);

CREATE TABLE `orderData` (
	`orderID` BINARY(20) NOT NULL,
	`userID` VARCHAR(20) NOT NULL,
	`orderDate` TIMESTAMP NOT NULL,
	`productID` BINARY(20) NOT NULL,
	`quantity` INT NOT NULL,
	`amount` INT NOT NULL,
	`sellingPrice` FLOAT NOT NULL,
	PRIMARY KEY (`orderID`)
) ENGINE=InnoDB;

CREATE TABLE `paymentData` (
	`paymentID` BINARY(20) NOT NULL,
	`razorpayID` VARCHAR(100) NOT NULL,
	`userID` VARCHAR(20) NOT NULL,
	`amount` FLOAT NOT NULL,
	`paymentDate` TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
	`status` VARCHAR(20) NOT NULL,
	PRIMARY KEY (`paymentID`)
) ENGINE=InnoDB;

CREATE TABLE `productsData` (
	`productID` BINARY(20) NOT NULL,
	`productName` VARCHAR(100) NOT NULL,
	PRIMARY KEY (`productID`)
) ENGINE=InnoDB;

INSERT INTO `productsData` (productID, productName) VALUES (UUID_TO_BIN(UUID()), "Roma 2.1");
INSERT INTO `productsData` (productID, productName) VALUES (UUID_TO_BIN(UUID()), "Roma 2.4");
INSERT INTO `productsData` (productID, productName) VALUES (UUID_TO_BIN(UUID()), "Roma Double");
INSERT INTO `productsData` (productID, productName) VALUES (UUID_TO_BIN(UUID()), "Buddy");
INSERT INTO `productsData` (productID, productName) VALUES (UUID_TO_BIN(UUID()), "USB Port");