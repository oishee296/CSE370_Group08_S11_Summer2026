-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 31, 2026 at 06:47 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `disaster management`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `Username` varchar(50) NOT NULL,
  `dept` varchar(30) NOT NULL,
  `adminID` int(15) NOT NULL,
  `accessLevel` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`Username`, `dept`, `adminID`, `accessLevel`) VALUES
('shadeed', 'Logistics Management', 101, 'Standard'),
('oishee', 'Field Operations', 102, 'Standard'),
('aryan', 'General Relief', 103, 'Standard');

-- --------------------------------------------------------

--
-- Table structure for table `admin_manages_dzones_and_invitems`
--

CREATE TABLE `admin_manages_dzones_and_invitems` (
  `Username` varchar(30) NOT NULL,
  `ZoneId` int(15) NOT NULL,
  `ItemId` int(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `Username` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`Username`) VALUES
('arshn'),
('v1'),
('v10'),
('v2'),
('v3'),
('v4'),
('v5'),
('v6'),
('v7'),
('v8'),
('v9');

-- --------------------------------------------------------

--
-- Table structure for table `deployment_history`
--

CREATE TABLE `deployment_history` (
  `HistoryID` int(15) NOT NULL,
  `VolunteerID` int(15) NOT NULL,
  `hours_earned` bigint(20) NOT NULL,
  `completion_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `deployment_history`
--

INSERT INTO `deployment_history` (`HistoryID`, `VolunteerID`, `hours_earned`, `completion_date`) VALUES
(1, 204, 1, '2026-08-31 12:30:23'),
(2, 204, 1, '2026-08-31 14:12:15'),
(3, 206, 1, '2026-08-31 14:17:49'),
(4, 204, 1, '2026-08-31 15:13:52'),
(5, 208, 2, '2026-08-31 15:13:59'),
(6, 204, 1, '2026-08-31 15:15:29');

-- --------------------------------------------------------

--
-- Table structure for table `disasterzones`
--

CREATE TABLE `disasterzones` (
  `ZoneId` int(15) NOT NULL,
  `status` varchar(15) NOT NULL,
  `name` varchar(30) NOT NULL,
  `location` varchar(50) NOT NULL,
  `severity` int(10) NOT NULL,
  `warehouseID` varchar(20) NOT NULL,
  `dispatchTimeStamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `disasterzones`
--

INSERT INTO `disasterzones` (`ZoneId`, `status`, `name`, `location`, `severity`, `warehouseID`, `dispatchTimeStamp`) VALUES
(1, 'Dispatched', 'Flood Rescue', 'Sector 4, Riverside', 8, '1', '2026-08-31 10:17:50'),
(2, 'Active', 'Cyclone Relief', 'Coastal Station B', 9, '2', '2026-08-30 14:17:38'),
(3, 'Standby', 'Wildfire Containment', 'North Forest Ridge', 5, '1', '2026-08-30 14:17:38');

-- --------------------------------------------------------

--
-- Table structure for table `inventoryitems`
--

CREATE TABLE `inventoryitems` (
  `ItemId` int(15) NOT NULL,
  `ExpirationDate` date NOT NULL,
  `Quantity` bigint(20) NOT NULL,
  `Category` varchar(30) NOT NULL,
  `ItemName` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `inventoryitems`
--

INSERT INTO `inventoryitems` (`ItemId`, `ExpirationDate`, `Quantity`, `Category`, `ItemName`) VALUES
(1, '2027-12-05', 0, 'grains(kg)', 'brown rice'),
(2, '2026-09-10', 23, 'dry', 'cookies'),
(3, '2026-09-02', 5, 'fruit', 'apples'),
(4, '2026-08-20', 15, 'liquid', 'milk'),
(6, '2033-06-14', 5, '?', 'candles');

-- --------------------------------------------------------

--
-- Table structure for table `shipmentlog`
--

CREATE TABLE `shipmentlog` (
  `ShipmentID` int(15) NOT NULL,
  `ItemId` int(15) NOT NULL,
  `ZoneId` int(15) NOT NULL,
  `WID` int(15) NOT NULL,
  `QuantityShipped` bigint(20) NOT NULL,
  `DispatchedBy` varchar(50) NOT NULL,
  `DispatchedAt` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shipmentlog`
--

INSERT INTO `shipmentlog` (`ShipmentID`, `ItemId`, `ZoneId`, `WID`, `QuantityShipped`, `DispatchedBy`, `DispatchedAt`) VALUES
(1, 3, 1, 1, 5, 'aryan', '2026-08-31 10:17:50');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) NOT NULL,
  `isActive` tinyint(1) DEFAULT 1,
  `regDate` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`username`, `password`, `isActive`, `regDate`) VALUES
('arshn', 'arshn', 1, '2026-08-30 16:21:09'),
('aryan', '48', 1, '2026-08-30 16:06:32'),
('oishee', '62', 1, '2026-08-30 16:06:32'),
('shadeed', '74', 1, '2026-08-30 16:06:32'),
('v1', 'v1', 1, '2026-08-31 12:22:24'),
('v10', 'v10', 1, '2026-08-31 12:22:24'),
('v2', 'v2', 1, '2026-08-31 12:22:24'),
('v3', 'v3', 1, '2026-08-31 12:22:24'),
('v4', 'v4', 1, '2026-08-31 12:22:24'),
('v5', 'v5', 1, '2026-08-31 12:22:24'),
('v6', 'v6', 1, '2026-08-31 12:22:24'),
('v7', 'v7', 1, '2026-08-31 12:22:24'),
('v8', 'v8', 1, '2026-08-31 12:22:24'),
('v9', 'v9', 1, '2026-08-31 12:22:24');

-- --------------------------------------------------------

--
-- Table structure for table `volunteers`
--

CREATE TABLE `volunteers` (
  `Username` varchar(30) NOT NULL,
  `VolunteerID` int(15) NOT NULL,
  `FullName` varchar(50) NOT NULL,
  `AvailabilityStatus` varchar(20) NOT NULL,
  `VolunteerType` varchar(20) NOT NULL,
  `specialty` varchar(30) NOT NULL,
  `certificationLevel` varchar(30) NOT NULL,
  `medicalSpecialty` varchar(30) NOT NULL,
  `license` varchar(25) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `volunteers`
--

INSERT INTO `volunteers` (`Username`, `VolunteerID`, `FullName`, `AvailabilityStatus`, `VolunteerType`, `specialty`, `certificationLevel`, `medicalSpecialty`, `license`) VALUES
('v1', 201, 'Volunteer1', 'Deployed', 'Field Support', 'Search & Rescue', 'Level 2 (Intermediate)', '', ''),
('v2', 202, 'Volunteer2', 'Available', 'Medical Support', 'First Aid', 'Level 3 (Advanced)', 'Emergency Nursing', 'RN-9942'),
('v3', 203, 'Volunteer3', 'Deployed', 'Logistics', 'Supply Management', 'Level 1 (Entry)', '', ''),
('v4', 204, 'Volunteer4', 'Available', 'Field Support', 'Flood Response', 'Level 2 (Intermediate)', '', ''),
('v5', 205, 'Volunteer5', 'Available', 'Medical Support', 'Triage', 'Level 3 (Advanced)', 'Paramedic', 'EMT-8831'),
('v6', 206, 'Volunteer6', 'Available', 'Shelter Management', 'Mass Care', 'Level 1 (Entry)', '', ''),
('v7', 207, 'Volunteer7', 'Deployed', 'Field Support', 'Search & Rescue', 'Level 3 (Advanced)', '', ''),
('v8', 208, 'Volunteer8', 'Deployed', 'Logistics', 'Communications', 'Level 1 (Entry)', '', ''),
('v9', 209, 'Volunteer9', 'Deployed', 'Medical Support', 'Psychological First Aid', 'Level 2 (Intermediate)', 'Mental Health', 'MH-1102'),
('v10', 210, 'Volunteer10', 'Available', 'Field Support', 'Debris Clearance', 'Level 1 (Entry)', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `volunteers_deployedto_dzones`
--

CREATE TABLE `volunteers_deployedto_dzones` (
  `VolunteerID` int(15) NOT NULL,
  `ZoneId` int(15) NOT NULL,
  `current_role` varchar(30) NOT NULL,
  `hours_contributed` bigint(20) NOT NULL,
  `deployed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `volunteers_deployedto_dzones`
--

INSERT INTO `volunteers_deployedto_dzones` (`VolunteerID`, `ZoneId`, `current_role`, `hours_contributed`, `deployed_at`) VALUES
(208, 2, 'Communications', 0, '2026-08-31 16:02:45'),
(207, 2, 'Search & Rescue', 0, '2026-08-31 16:44:03'),
(201, 1, 'Search & Rescue', 0, '2026-08-31 16:44:10'),
(209, 2, 'Emergency Driver', 0, '2026-08-31 16:44:19'),
(203, 2, 'Supply Management', 0, '2026-08-31 16:44:28');

-- --------------------------------------------------------

--
-- Table structure for table `warehouses`
--

CREATE TABLE `warehouses` (
  `WID` int(15) NOT NULL,
  `Manager` varchar(30) NOT NULL,
  `Capacity` bigint(20) NOT NULL,
  `Contact` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `warehouses`
--

INSERT INTO `warehouses` (`WID`, `Manager`, `Capacity`, `Contact`) VALUES
(1, 'Ira', 150, 1234),
(2, 'Hasib', 50, 456);

-- --------------------------------------------------------

--
-- Table structure for table `warehouse_contains_inventoryitems`
--

CREATE TABLE `warehouse_contains_inventoryitems` (
  `ItemId` int(15) NOT NULL,
  `WID` int(15) NOT NULL,
  `shelf_location` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `warehouse_contains_inventoryitems`
--

INSERT INTO `warehouse_contains_inventoryitems` (`ItemId`, `WID`, `shelf_location`) VALUES
(3, 1, 'A1'),
(6, 1, 'C3');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD KEY `fk_admin_user` (`Username`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD KEY `fk_customer_user` (`Username`);

--
-- Indexes for table `deployment_history`
--
ALTER TABLE `deployment_history`
  ADD PRIMARY KEY (`HistoryID`);

--
-- Indexes for table `disasterzones`
--
ALTER TABLE `disasterzones`
  ADD PRIMARY KEY (`ZoneId`);

--
-- Indexes for table `inventoryitems`
--
ALTER TABLE `inventoryitems`
  ADD PRIMARY KEY (`ItemId`);

--
-- Indexes for table `shipmentlog`
--
ALTER TABLE `shipmentlog`
  ADD PRIMARY KEY (`ShipmentID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`username`);

--
-- Indexes for table `warehouses`
--
ALTER TABLE `warehouses`
  ADD PRIMARY KEY (`WID`);

--
-- Indexes for table `warehouse_contains_inventoryitems`
--
ALTER TABLE `warehouse_contains_inventoryitems`
  ADD PRIMARY KEY (`ItemId`,`WID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `deployment_history`
--
ALTER TABLE `deployment_history`
  MODIFY `HistoryID` int(15) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `disasterzones`
--
ALTER TABLE `disasterzones`
  MODIFY `ZoneId` int(15) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `inventoryitems`
--
ALTER TABLE `inventoryitems`
  MODIFY `ItemId` int(15) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `shipmentlog`
--
ALTER TABLE `shipmentlog`
  MODIFY `ShipmentID` int(15) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `warehouses`
--
ALTER TABLE `warehouses`
  MODIFY `WID` int(15) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin`
--
ALTER TABLE `admin`
  ADD CONSTRAINT `fk_admin_user` FOREIGN KEY (`Username`) REFERENCES `user` (`username`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `customer`
--
ALTER TABLE `customer`
  ADD CONSTRAINT `fk_customer_user` FOREIGN KEY (`Username`) REFERENCES `user` (`username`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
