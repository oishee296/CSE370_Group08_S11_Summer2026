-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 28, 2026 at 04:52 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

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
  `Username` varchar(30) NOT NULL,
  `dept` varchar(30) NOT NULL,
  `adminID` int(15) NOT NULL,
  `accessLevel` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`Username`, `dept`, `adminID`, `accessLevel`) VALUES
('oisheetesting', 'General Relief', 0, 'Standard');

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
  `Username` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`Username`) VALUES
('oisheecustomer');

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

-- --------------------------------------------------------

--
-- Table structure for table `donor`
--

CREATE TABLE `donor` (
  `Username` int(15) NOT NULL,
  `DonorType` varchar(30) NOT NULL,
  `NGOtierRanking` varchar(30) NOT NULL,
  `orgID` int(15) NOT NULL,
  `corporateTierRanking` varchar(30) NOT NULL,
  `companySize` bigint(20) NOT NULL,
  `taxID` int(15) NOT NULL,
  `bloodGroup` varchar(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
(0, '2027-12-05', 10, 'grains(kg)', 'brown rice'),
(0, '2028-12-09', 20, 'dry', 'biscuits'),
(0, '2026-09-02', 2, 'fruit', 'apples'),
(0, '2026-08-20', 5, 'liquid', 'milk');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `isActive` tinyint(1) DEFAULT 1,
  `regDate` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`username`, `password`, `isActive`, `regDate`) VALUES
('aarshan', '24', 1, '2026-08-08 05:52:39'),
('aryan007', '23', 1, '2026-08-08 06:01:28'),
('hasib', '16', 1, '2026-08-18 05:25:57'),
('oishee296', '25', 1, '2026-08-08 05:35:54'),
('oisheecustomer', '123', 1, '2026-08-27 14:20:03'),
('oisheetesting', '123', 1, '2026-08-27 12:08:03');

-- --------------------------------------------------------

--
-- Table structure for table `usersession`
--

CREATE TABLE `usersession` (
  `sessionID` varchar(15) NOT NULL,
  `IPaddress` varchar(30) NOT NULL,
  `LoginTimestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `LogoutTimestamp` timestamp NULL DEFAULT NULL,
  `sessionUserName` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

-- --------------------------------------------------------

--
-- Table structure for table `volunteers_deployedto_dzones`
--

CREATE TABLE `volunteers_deployedto_dzones` (
  `VolunteerID` int(15) NOT NULL,
  `ZoneId` int(15) NOT NULL,
  `current_role` varchar(30) NOT NULL,
  `hours_contributed` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
-- Indexes for dumped tables
--

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`username`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
