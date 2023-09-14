-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 06, 2022 at 02:58 AM
-- Server version: 5.7.36
-- PHP Version: 7.4.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `airsystem`
--

-- --------------------------------------------------------

--
-- Table structure for table `airline`
--

DROP TABLE IF EXISTS `airline`;
CREATE TABLE IF NOT EXISTS `airline` (
  `airline_name` varchar(20) NOT NULL,
  PRIMARY KEY (`airline_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('China Eastern'),
('Singapore Air');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

DROP TABLE IF EXISTS `airline_staff`;
CREATE TABLE IF NOT EXISTS `airline_staff` (
  `username` varchar(32) NOT NULL,
  `s_password` varchar(200) DEFAULT NULL,
  `airline_name` varchar(20) DEFAULT NULL,
  `first_name` varchar(20) NOT NULL,
  `last_name` varchar(20) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`username`),
  KEY `airline_name` (`airline_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `s_password`, `airline_name`, `first_name`, `last_name`, `date_of_birth`) VALUES
('tc9152', 'tc19782244', 'China Eastern', 'Timothy', 'Charleson', '1978-08-07'),
('asdfsd', 'fgn', 'China Eastern', 'Shane', 'Tom', '2022-04-06'),
('test', 'test', 'China Eastern', 'tester', 'testy', '2022-04-29');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff_phone_number`
--

DROP TABLE IF EXISTS `airline_staff_phone_number`;
CREATE TABLE IF NOT EXISTS `airline_staff_phone_number` (
  `username` varchar(32) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  PRIMARY KEY (`username`,`phone_number`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline_staff_phone_number`
--

INSERT INTO `airline_staff_phone_number` (`username`, `phone_number`) VALUES
('tc9152', '9186552837');

-- --------------------------------------------------------

--
-- Table structure for table `airplane`
--

DROP TABLE IF EXISTS `airplane`;
CREATE TABLE IF NOT EXISTS `airplane` (
  `airplane_id` varchar(20) NOT NULL,
  `num_of_seats` int(11) DEFAULT NULL,
  `manufacturer` varchar(50) DEFAULT NULL,
  `age` varchar(20) DEFAULT NULL,
  `airline_name` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`airplane_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`airplane_id`, `num_of_seats`, `manufacturer`, `age`, `airline_name`) VALUES
('747-400', 568, 'Boeing Commercial Airplanes', '28', 'China Eastern'),
('A380', 525, 'Airbus', '17', 'China Eastern'),
('A340-500', 313, 'Airbus', '15', 'China Eastern');

-- --------------------------------------------------------

--
-- Table structure for table `airport`
--

DROP TABLE IF EXISTS `airport`;
CREATE TABLE IF NOT EXISTS `airport` (
  `airport_code` varchar(5) NOT NULL,
  `airport_name` varchar(50) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`airport_code`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`airport_code`, `airport_name`, `country`, `city`, `type`) VALUES
('JFK', 'John F. Kennedy International Airport', 'United States of America', 'New York City', 'Both'),
('PVG', 'Shanghai Pudong International Airport', 'China', 'Shanghai', 'International'),
('LGA', 'LaGuardia Airport', 'United States of America', 'New York City', 'International');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
CREATE TABLE IF NOT EXISTS `customer` (
  `email` varchar(50) NOT NULL,
  `first_name` varchar(20) NOT NULL,
  `last_name` varchar(20) NOT NULL,
  `c_password` varchar(200) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `street` varchar(50) DEFAULT NULL,
  `building_number` varchar(10) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `passport_number` varchar(20) DEFAULT NULL,
  `passport_expiration` date DEFAULT NULL,
  `passport_country` varchar(50) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `first_name`, `last_name`, `c_password`, `state`, `city`, `street`, `building_number`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('carlT@hotmail.com', 'Carl', 'Thorne', 'paSsword', 'Arkansas', 'Conway', 'Christian Street', '1918', '5016612021', 'Q12438925', '2025-07-14', 'United States of America', '1918-02-11'),
('sallyM@yahoo.com', 'Sally', 'Margarine', 'apple38', 'Montana', 'Lewis Town', 'West Pine Street', '509', '4063244777', 'P05937291', '2022-08-22', 'United States of America', '1975-12-31'),
('trevrP@gmail.com', 'Trevor', 'Pine', 'skateislove1', 'California', 'Bakersfield', 'L Street', '1309', '6614446422', 'R19357534', '2027-04-20', 'United States of America', '1989-04-19'),
('test@test.com', 'firstname', 'lastname', 'test', 'New York', 'New York City', 'Broadway', '123', '1111111111', 'pas234f', '2022-04-22', 'America', '2022-02-22');

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

DROP TABLE IF EXISTS `flight`;
CREATE TABLE IF NOT EXISTS `flight` (
  `flight_number` varchar(10) NOT NULL,
  `flight_status` varchar(10) DEFAULT NULL,
  `departure_date_time` varchar(20) NOT NULL,
  `airline_name` varchar(20) NOT NULL,
  `airplane_id` varchar(20) DEFAULT NULL,
  `departure_airport_code` varchar(5) DEFAULT NULL,
  `arrival_airport_code` varchar(5) DEFAULT NULL,
  `arrival_date_time` varchar(20) DEFAULT NULL,
  `base_price` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`flight_number`,`departure_date_time`,`airline_name`),
  KEY `airline_name` (`airline_name`),
  KEY `airplane_id` (`airplane_id`),
  KEY `departure_airport_code` (`departure_airport_code`,`arrival_airport_code`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`flight_number`, `flight_status`, `departure_date_time`, `airline_name`, `airplane_id`, `departure_airport_code`, `arrival_airport_code`, `arrival_date_time`, `base_price`) VALUES
('102', 'On-time', '2022-04-01 13:27:00', 'China Eastern', 'A340-500', 'JFK', 'PVG', '2022-04-02 15:02:00', '500.00'),
('103', 'Delayed', '2022-04-06 08:15:00', 'China Eastern', '747-400', 'PVG', 'JFK', '2022-04-09 02:36:00', '585.00'),
('104', 'On-time', '2022-04-12 12:00:00', 'China Eastern', '747-400', 'JFK', 'PVG', '2022-04-13 13:15:00', '650.00'),
('999', 'On-Time', '2022-04-01 20:45:09', 'Singapore Air', 'A999', 'JFK', 'LGA', '2022-04-01 20:45:09', '123.45'),
('998', 'Delayed', '2022-05-05 21:14:46', 'Delta', 'TSTPI', 'LGA', 'PVG', '2022-05-10 21:14:46', '509.73'),
('329', 'On-time', '2022-05-02', 'fdsa', 'fdsaf', 'fdsaf', 'fds', '2022-05-27', '23.00');

-- --------------------------------------------------------

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
CREATE TABLE IF NOT EXISTS `ratings` (
  `flight_number` varchar(10) DEFAULT NULL,
  `customer_email` varchar(50) NOT NULL,
  `rating` float DEFAULT NULL,
  `comments` tinytext,
  PRIMARY KEY (`customer_email`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
CREATE TABLE IF NOT EXISTS `ticket` (
  `ticket_id` varchar(20) NOT NULL,
  `customer_email` varchar(50) DEFAULT NULL,
  `travel_class` varchar(20) DEFAULT NULL,
  `airline_name` varchar(20) DEFAULT NULL,
  `flight_number` varchar(10) DEFAULT NULL,
  `departure_date_time` datetime DEFAULT NULL,
  `sold_price` decimal(6,2) DEFAULT NULL,
  `purchase_date_time` datetime DEFAULT NULL,
  `card_type` varchar(32) DEFAULT NULL,
  `name_on_card` varchar(40) DEFAULT NULL,
  `expiration_date` date DEFAULT NULL,
  PRIMARY KEY (`ticket_id`),
  KEY `customer_email` (`customer_email`),
  KEY `airline_name` (`airline_name`),
  KEY `flight_number` (`flight_number`,`departure_date_time`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `customer_email`, `travel_class`, `airline_name`, `flight_number`, `departure_date_time`, `sold_price`, `purchase_date_time`, `card_type`, `name_on_card`, `expiration_date`) VALUES
('1200546', 'carlT@hotmail.com', 'Economy Class', 'China Eastern', '102', '2022-04-01 13:27:00', '540.39', '2022-01-26 20:57:38', 'Credit', 'Carl Thorne', '2025-04-01'),
('5438554', 'sallyM@yahoo.com', 'Business Class', 'China Eastern', '104', '2022-04-12 12:00:00', '742.12', '2022-03-30 09:23:12', 'Debit', 'Sally Margarine', '2027-02-01'),
('9237545', 'trevrP@gmail.com', 'First class', 'China Eastern', '103', '2022-04-06 08:15:00', '1244.00', '2021-12-24 02:01:19', 'Debit', 'Trevor Pine', '2022-05-01'),
('1758969', 'test@test.com', 'Economy Class', 'fdsa', '329', '2022-05-02 00:00:00', '23.00', '2022-05-01 14:18:07', 'Debit', 'fdsa', '2022-05-01'),
('3224717', 'test@test.com', 'First Class', 'Delta', '998', '2022-05-05 21:14:46', '1529.19', '2022-05-05 22:40:41', 'Credit', 'testytest', '2024-07-01'),
('2905060', 'test@test.com', 'First Class', 'fdsa', '329', '2022-05-02 00:00:00', '23.00', '2022-05-01 18:57:46', 'Credit', 'asdf', '2022-05-01'),
('7172109', 'test@test.com', 'Economy Class', 'Delta', '998', '2022-05-05 21:14:46', '509.73', '2022-05-05 18:58:04', 'Credit', 'sa', '2022-05-01'),
('8444811', 'test@test.com', 'First Class', 'Delta', '998', '2022-05-05 21:14:46', '1529.19', '2022-05-05 22:41:17', 'Debit', 'testytesttestestest', '2024-06-01');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
