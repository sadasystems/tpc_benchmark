-- TPC-H
-- Create Table Clone - no clustering or partitioning
--
CREATE TABLE `_destination_dataset.lineitem`
AS 
SELECT * FROM `_source_dataset.lineitem`;

CREATE TABLE `_destination_dataset.orders`
AS 
SELECT * FROM `_source_dataset.orders`;

CREATE TABLE `_destination_dataset.partsupp`
AS 
SELECT * FROM `_source_dataset.partsupp`;

CREATE TABLE `_destination_dataset.part`
AS 
SELECT * FROM `_source_dataset.part`;

CREATE TABLE `_destination_dataset.customer`
AS 
SELECT * FROM `_source_dataset.customer`;

CREATE TABLE `_destination_dataset.supplier`
AS 
SELECT * FROM `_source_dataset.supplier`;

CREATE TABLE `_destination_dataset.nation`
AS 
SELECT * FROM `_source_dataset.nation`;

CREATE TABLE `_destination_dataset.region`
AS 
SELECT * FROM `_source_dataset.region`;
