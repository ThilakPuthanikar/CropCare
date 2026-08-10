-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Jun 12, 2026 at 02:27 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cropcare_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'admin',
  `is_approved` tinyint(1) NOT NULL DEFAULT 1,
  `profile_photo` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`id`, `name`, `email`, `password_hash`, `role`, `is_approved`, `profile_photo`, `created_at`, `updated_at`) VALUES
(1, 'Admin User', 'admin@cropcare.com', '$2a$12$gL0t3BogaBEplHGf8hFy2uEWq1dBXJYl7Q1LjFL3jMVPJqJ5dX.1e', 'admin', 1, NULL, '2026-05-30 08:57:06', '2026-05-30 08:57:06');

-- --------------------------------------------------------

--
-- Table structure for table `ads`
--

CREATE TABLE `ads` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` varchar(1000) NOT NULL,
  `image_url` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ads`
--

INSERT INTO `ads` (`id`, `title`, `content`, `image_url`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'Premium Fertilizer Offer', 'Get 20% discount on premium organic fertilizers this month!', NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06');

-- --------------------------------------------------------

--
-- Table structure for table `crop_plans`
--

CREATE TABLE `crop_plans` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `crop` varchar(100) NOT NULL,
  `planting_date` date NOT NULL,
  `harvest_date` date NOT NULL,
  `duration_days` int(11) NOT NULL,
  `reminders_json` text DEFAULT NULL,
  `stages_json` longtext NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crop_plans`
--

INSERT INTO `crop_plans` (`id`, `user_id`, `crop`, `planting_date`, `harvest_date`, `duration_days`, `reminders_json`, `stages_json`, `created_at`, `updated_at`) VALUES
(1, 6, 'tomato', '2026-06-20', '2026-10-27', 130, '{\"watering\": true, \"fertilizing\": true, \"pest_control\": true, \"pruning\": true}', '[{\"title\": \"Nursery and field preparation\", \"description\": \"Prepare healthy seedlings and a well-drained transplant field.\", \"day_range\": \"1-21\", \"start_date\": \"2026-06-20\", \"end_date\": \"2026-07-10\", \"tasks\": [\"Raise healthy seedlings and prepare the transplant field.\", \"Apply starter nutrients before shifting seedlings.\", \"Ensure drainage is ready before planting.\"]}, {\"title\": \"Transplant establishment\", \"description\": \"Reduce shock and maintain early survival after transplanting.\", \"day_range\": \"22-44\", \"start_date\": \"2026-07-11\", \"end_date\": \"2026-08-02\", \"tasks\": [\"Transplant healthy seedlings at the right spacing.\", \"Irrigate immediately and reduce transplant shock.\", \"Watch for wilt, collar issues, and stand loss.\"]}, {\"title\": \"Vegetative growth\", \"description\": \"Support canopy build, staking, and regular nutrient supply.\", \"day_range\": \"45-73\", \"start_date\": \"2026-08-03\", \"end_date\": \"2026-08-31\", \"tasks\": [\"Apply split nutrients based on active crop demand.\", \"Maintain irrigation balance and avoid prolonged stress.\", \"Scout for weeds, pests, and nutrient deficiency symptoms.\"]}, {\"title\": \"Flowering and fruit set\", \"description\": \"Protect the crop during the most stress-sensitive stage.\", \"day_range\": \"74-102\", \"start_date\": \"2026-09-01\", \"end_date\": \"2026-09-29\", \"tasks\": [\"Avoid major moisture swings during flowering.\", \"Inspect for blossom drop, fruit damage, or foliar disease.\", \"Keep airflow and canopy health under control.\"]}, {\"title\": \"Fruit development and harvest\", \"description\": \"Maintain fruit quality and harvest in planned rounds.\", \"day_range\": \"103-130\", \"start_date\": \"2026-09-30\", \"end_date\": \"2026-10-27\", \"tasks\": [\"Support fruit fill with regular irrigation and nutrition.\", \"Harvest at the right market maturity stage.\", \"Sort damaged produce and maintain field sanitation.\"]}]', '2026-06-12 10:58:39', '2026-06-12 10:58:39');

-- --------------------------------------------------------

--
-- Table structure for table `mandi_prices`
--

CREATE TABLE `mandi_prices` (
  `id` int(11) NOT NULL,
  `crop_name` varchar(120) NOT NULL,
  `district` varchar(120) NOT NULL,
  `mandi_name` varchar(180) NOT NULL,
  `price_per_quintal` float NOT NULL,
  `min_price` float DEFAULT NULL,
  `max_price` float DEFAULT NULL,
  `price_date` date NOT NULL,
  `last_updated` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `variety` varchar(120) DEFAULT NULL,
  `grade` varchar(120) DEFAULT NULL,
  `arrival` float DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `mandi_prices`
--

INSERT INTO `mandi_prices` (`id`, `crop_name`, `district`, `mandi_name`, `price_per_quintal`, `min_price`, `max_price`, `price_date`, `last_updated`, `created_at`, `updated_at`, `variety`, `grade`, `arrival`, `unit`) VALUES
(1, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 1300, 1040, 1560, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(2, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 1450, 1190, 1710, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(3, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 1200, 940, 1460, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(4, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 1550, 1290, 1810, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(5, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 1800, 1540, 2060, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(6, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 2250, 1990, 2510, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(7, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 2050, 1790, 2310, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(8, 'Tomato', 'Bagalkot', 'Bagalkot APMC', 1880, 1620, 2140, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(9, 'Onion', 'Bagalkot', 'Bagalkot APMC', 1850, 1630, 2070, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(10, 'Onion', 'Bagalkot', 'Bagalkot APMC', 1780, 1560, 2000, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(11, 'Onion', 'Bagalkot', 'Bagalkot APMC', 1920, 1700, 2140, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(12, 'Onion', 'Bagalkot', 'Bagalkot APMC', 2080, 1860, 2300, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(13, 'Onion', 'Bagalkot', 'Bagalkot APMC', 2240, 2020, 2460, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(14, 'Onion', 'Bagalkot', 'Bagalkot APMC', 2410, 2190, 2630, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(15, 'Onion', 'Bagalkot', 'Bagalkot APMC', 2350, 2130, 2570, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(16, 'Onion', 'Bagalkot', 'Bagalkot APMC', 2190, 1970, 2410, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(17, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 5650, 5330, 5970, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(18, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 5710, 5390, 6030, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(19, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 5780, 5460, 6100, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(20, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 5820, 5500, 6140, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(21, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 5890, 5570, 6210, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(22, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 5980, 5660, 6300, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(23, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 6070, 5750, 6390, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(24, 'Groundnut', 'Bagalkot', 'Bagalkot APMC', 6010, 5690, 6330, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(25, 'Paddy', 'Mysuru', 'Mysuru APMC', 2240, 2100, 2380, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(26, 'Paddy', 'Mysuru', 'Mysuru APMC', 2280, 2140, 2420, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(27, 'Paddy', 'Mysuru', 'Mysuru APMC', 2260, 2120, 2400, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(28, 'Paddy', 'Mysuru', 'Mysuru APMC', 2310, 2170, 2450, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(29, 'Paddy', 'Mysuru', 'Mysuru APMC', 2350, 2210, 2490, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(30, 'Paddy', 'Mysuru', 'Mysuru APMC', 2390, 2250, 2530, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(31, 'Paddy', 'Mysuru', 'Mysuru APMC', 2370, 2230, 2510, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(32, 'Paddy', 'Mysuru', 'Mysuru APMC', 2420, 2280, 2560, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(33, 'Tomato', 'Mysuru', 'Mysuru APMC', 1450, 1170, 1730, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(34, 'Tomato', 'Mysuru', 'Mysuru APMC', 1620, 1340, 1900, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(35, 'Tomato', 'Mysuru', 'Mysuru APMC', 1380, 1100, 1660, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(36, 'Tomato', 'Mysuru', 'Mysuru APMC', 1710, 1430, 1990, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(37, 'Tomato', 'Mysuru', 'Mysuru APMC', 1980, 1700, 2260, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(38, 'Tomato', 'Mysuru', 'Mysuru APMC', 2440, 2160, 2720, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(39, 'Tomato', 'Mysuru', 'Mysuru APMC', 2210, 1930, 2490, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(40, 'Tomato', 'Mysuru', 'Mysuru APMC', 2050, 1770, 2330, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(41, 'Onion', 'Mysuru', 'Mysuru APMC', 1760, 1550, 1970, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(42, 'Onion', 'Mysuru', 'Mysuru APMC', 1820, 1610, 2030, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(43, 'Onion', 'Mysuru', 'Mysuru APMC', 1910, 1700, 2120, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(44, 'Onion', 'Mysuru', 'Mysuru APMC', 2050, 1840, 2260, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(45, 'Onion', 'Mysuru', 'Mysuru APMC', 2180, 1970, 2390, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(46, 'Onion', 'Mysuru', 'Mysuru APMC', 2340, 2130, 2550, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(47, 'Onion', 'Mysuru', 'Mysuru APMC', 2290, 2080, 2500, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(48, 'Onion', 'Mysuru', 'Mysuru APMC', 2140, 1930, 2350, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(49, 'Maize', 'Belagavi', 'Belagavi APMC', 1930, 1835, 2025, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(50, 'Maize', 'Belagavi', 'Belagavi APMC', 1950, 1855, 2045, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(51, 'Maize', 'Belagavi', 'Belagavi APMC', 1940, 1845, 2035, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(52, 'Maize', 'Belagavi', 'Belagavi APMC', 1970, 1875, 2065, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(53, 'Maize', 'Belagavi', 'Belagavi APMC', 1990, 1895, 2085, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(54, 'Maize', 'Belagavi', 'Belagavi APMC', 2010, 1915, 2105, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(55, 'Maize', 'Belagavi', 'Belagavi APMC', 2030, 1935, 2125, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(56, 'Maize', 'Belagavi', 'Belagavi APMC', 2050, 1955, 2145, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(57, 'Groundnut', 'Belagavi', 'Belagavi APMC', 5520, 5220, 5820, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(58, 'Groundnut', 'Belagavi', 'Belagavi APMC', 5600, 5300, 5900, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(59, 'Groundnut', 'Belagavi', 'Belagavi APMC', 5670, 5370, 5970, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(60, 'Groundnut', 'Belagavi', 'Belagavi APMC', 5750, 5450, 6050, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(61, 'Groundnut', 'Belagavi', 'Belagavi APMC', 5840, 5540, 6140, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(62, 'Groundnut', 'Belagavi', 'Belagavi APMC', 5920, 5620, 6220, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(63, 'Groundnut', 'Belagavi', 'Belagavi APMC', 6000, 5700, 6300, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(64, 'Groundnut', 'Belagavi', 'Belagavi APMC', 5950, 5650, 6250, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(65, 'Tomato', 'Belagavi', 'Belagavi APMC', 1220, 970, 1470, '2026-03-07', '2026-03-07 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(66, 'Tomato', 'Belagavi', 'Belagavi APMC', 1360, 1110, 1610, '2026-03-14', '2026-03-14 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(67, 'Tomato', 'Belagavi', 'Belagavi APMC', 1180, 930, 1430, '2026-03-21', '2026-03-21 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(68, 'Tomato', 'Belagavi', 'Belagavi APMC', 1490, 1240, 1740, '2026-03-28', '2026-03-28 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(69, 'Tomato', 'Belagavi', 'Belagavi APMC', 1730, 1480, 1980, '2026-04-04', '2026-04-04 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(70, 'Tomato', 'Belagavi', 'Belagavi APMC', 2140, 1890, 2390, '2026-04-11', '2026-04-11 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(71, 'Tomato', 'Belagavi', 'Belagavi APMC', 1960, 1710, 2210, '2026-04-18', '2026-04-18 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL),
(72, 'Tomato', 'Belagavi', 'Belagavi APMC', 1810, 1560, 2060, '2026-04-25', '2026-04-25 11:30:00', '2026-05-30 08:58:55', '2026-05-30 08:58:55', NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `schemes`
--

CREATE TABLE `schemes` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `type` varchar(50) NOT NULL DEFAULT 'national',
  `beneficiary` varchar(100) DEFAULT NULL,
  `benefits` text DEFAULT NULL,
  `eligibility` text DEFAULT NULL,
  `documents_required` text DEFAULT NULL,
  `steps_to_apply` text DEFAULT NULL,
  `duration` varchar(255) DEFAULT NULL,
  `official_link` varchar(500) DEFAULT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `district` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `schemes`
--

INSERT INTO `schemes` (`id`, `title`, `description`, `type`, `beneficiary`, `benefits`, `eligibility`, `documents_required`, `steps_to_apply`, `duration`, `official_link`, `icon`, `state`, `district`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'PM-KISAN Samman Nidhi', 'Direct income support scheme providing assured annual financial assistance to all eligible landholding farmer families across India via Direct Benefit Transfer (DBT).', 'national', 'small', 'Rs. 6,000 per financial year, transferred directly into bank accounts in three equal installments of Rs. 2,000 every 4 months.', 'All landholding farmer families with cultivable landholding in their names. Exclusions apply to institutional landholders, constitutional post holders, serving/retired government employees, doctors, engineers, lawyers, and income tax payers.', '[\"Aadhaar Card (mandatory for e-KYC and DBT link)\", \"Bank Account Details (Passbook copy showing account number and IFSC code)\", \"Land Ownership Records (Updated RTC / Khata / RoR - Record of Rights showing survey number and ownership)\", \"Active Mobile Number linked with Aadhaar\"]', '[\"Step 1: Portal or Center Visit - Visit the official portal https://pmkisan.gov.in/ and click on \'New Farmer Registration\', or visit your nearest Common Service Center (CSC) / Raitha Samparka Kendra (RSK).\", \"Step 2: Land & Personal Data Entry - Select Rural/Urban farmer registration, enter your Aadhaar number, state (Karnataka), and mobile number. Input your exact land details including Survey Number, Dag Number, and Khata Area.\", \"Step 3: Document Upload - Upload clear scanned copies of your land ownership proof (RTC/RoR) and Aadhaar card.\", \"Step 4: Mandatory e-KYC Completion - Complete OTP-based e-KYC on the portal or biometric e-KYC at a CSC to link your Aadhaar with DBT payment routing.\", \"Step 5: Verification & Payment Tracking - Your local agriculture department and revenue officers verify land ownership against the state Bhoomi database. Once approved, track your installment status under \'Beneficiary Status\' on the portal.\"]', 'Ongoing Annual Benefit', 'https://pmkisan.gov.in/', 'fas fa-rupee-sign', NULL, NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(2, 'Pradhan Mantri Fasal Bima Yojana', 'Flagship comprehensive crop insurance scheme providing risk coverage from pre-sowing to post-harvest against natural calamities, pests, and diseases.', 'national', 'general', 'Comprehensive insurance coverage for crop loss. Highly subsidized farmer premium: only 2% for Kharif crops, 1.5% for Rabi crops, and 5% for annual commercial/horticultural crops.', 'All farmers growing notified crops in notified insurance areas (districts/taluks). Both loanee (KCC) and non-loanee farmers (including sharecroppers and tenant farmers with valid tenancy agreements) are eligible.', '[\"Aadhaar Card\", \"Bank Account Passbook (showing account number and IFSC code)\", \"Land Records (RTC / Khata / Pahani / Sowing Certificate from Village Accountant or Revenue Officer)\", \"Crop Sowing Declaration (or self-declaration of sowing date and crop variety)\", \"Tenancy / Sharecropper Agreement (if cultivating leased land)\"]', '[\"Step 1: Check Notification & Cut-off Dates - Verify that your crop and district/taluk are notified for the current Kharif/Rabi season before the enrollment deadline (usually July 31 for Kharif and December 31 for Rabi).\", \"Step 2: Choose Application Channel - Apply online via https://pmfby.gov.in/, through Samrakshane (Karnataka state portal), at a primary agricultural cooperative bank (PACS), or at a Common Service Center (CSC).\", \"Step 3: Submit Crop & Land Details - Enter your Survey Number, notified crop name, area sown in hectares, and bank details.\", \"Step 4: Pay Subsidized Premium - Pay your share of the insurance premium (1.5% to 5%) online or at the bank counter and receive an official policy receipt (Acknowledge ID).\", \"Step 5: Claim Filing & Settlement - In case of localized crop loss or mid-season adversity, intimate the insurance company or agriculture officer within 72 hours via the Crop Insurance App/Toll-Free Helpline with geotagged photos of the damaged crop for survey and claim payout.\"]', 'Seasonal (Kharif / Rabi cycle)', 'https://pmfby.gov.in/', 'fas fa-shield-alt', NULL, NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(3, 'Kisan Credit Card', 'Institutional short-term crop credit and working capital support mechanism enabling farmers to purchase agricultural inputs and meet farming expenses at subsidized interest rates.', 'national', 'general', 'Short-term crop loans up to Rs. 3 Lakhs at a subsidized interest rate of 7% per annum. Prompt repayment within the due date earns an additional 3% interest subvention, lowering the effective interest rate to just 4% per annum. Collateral-free loan limit up to Rs. 1.60 Lakhs.', 'Individual farmers, joint borrowers, tenant farmers, sharecroppers, and Self-Help Groups (SHGs) involved in agricultural production or allied activities (dairy, poultry, fisheries).', '[\"Identity Proof (Aadhaar Card, Voter ID, PAN Card, or Driving License)\", \"Address Proof (Aadhaar Card or Utility Bill)\", \"Land Records (Updated RTC / Khata showing landholding and encumbrance status)\", \"Cropping Plan (Details of crops grown across Kharif and Rabi seasons)\", \"2 Passport-size Photographs\"]', '[\"Step 1: Obtain KCC Application Form - Download the simplified 1-page KCC application form from https://www.myscheme.gov.in/schemes/kcc or visit your commercial bank, Regional Rural Bank (Karnataka Gramin Bank), or cooperative bank branch.\", \"Step 2: Fill Cropping & Credit Requirements - List the crops you plan to grow, acreage, and estimated operational costs for seeds, fertilizers, and labor.\", \"Step 3: Submit Land & Verification Documents - Attach your updated land records (RTC) and Aadhaar card at the bank branch.\", \"Step 4: Bank Inspection & Limit Sanction - The bank field officer verifies your cultivation records and calculates your scale of finance credit limit.\", \"Step 5: Card Activation & Drawal - Receive your KCC RuPay ATM/Debit card and passbook to withdraw working capital directly from ATMs or purchase agricultural inputs from authorized dealers.\"]', 'Renewable 5-Year Credit Limit (Annual Review)', 'https://www.myscheme.gov.in/schemes/kcc', 'fas fa-credit-card', NULL, NULL, 1, '2026-05-30 08:58:55', '2026-05-30 08:58:55'),
(4, 'PM-KUSUM Scheme (Component B)', 'Clean energy agricultural irrigation initiative providing heavy financial subsidies for setting up standalone off-grid solar-powered agriculture pumps.', 'national', 'small', '60% capital subsidy (30% Central + 30% State) on standalone off-grid Solar Agriculture Pumps (up to 7.5 HP capacity). Farmers pay only 10% upfront beneficiary contribution, while the remaining 30% is provided as an institutional bank loan.', 'Individual farmers, Water User Associations, and Farmer Producer Organizations (FPOs) who own cultivable land with a water source (borewell, open well, or farm pond) without an existing grid-connected electric pump connection.', '[\"Aadhaar Card\", \"Land Ownership Record (RTC / Khata copy)\", \"Bank Account Passbook copy\", \"Certificate of Water Source (Borewell depth / yield confirmation or open well details)\", \"Passport-size Photograph\"]', '[\"Step 1: Check State Portal Registration - In Karnataka, applications for PM-KUSUM are processed via the Karnataka Renewable Energy Development Limited (KREDL) or ESCOM (BESCOM/HESCOM) portal when registration windows open.\", \"Step 2: Submit Application & Pump Specifications - Select your required pump capacity (3 HP, 5 HP, or 7.5 HP - surface or submersible) corresponding to your water source depth and land area.\", \"Step 3: Document Verification & Technical Feasibility - State technical officers verify land ownership and water source availability on your farmland.\", \"Step 4: Pay 10% Beneficiary Share - Once sanctioned and the demand note is issued, deposit your 10% beneficiary contribution online to the designated state agency account.\", \"Step 5: Installation & Inspection - Authorized vendors install the solar panel arrays, controller, and pump set on your farm, followed by joint commissioning inspection and 5-year warranty activation.\"]', 'Capital Subsidy + 5-Year Vendor Warranty', 'https://pmkusum.mnre.gov.in/', 'fas fa-solar-panel', NULL, NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(5, 'Soil Health Card Scheme', 'Scientific soil testing and nutrient management advisory program providing farm-specific fertilizer prescriptions to optimize crop yield and prevent soil degradation.', 'national', 'general', 'Free comprehensive lab testing of soil samples across 12 vital macro and micro parameters (pH, EC, Organic Carbon, Available N, P, K, S, Zn, Fe, Cu, Mn, and B). Provides a tailored Soil Health Card with specific fertilizer and organic amendment dosage recommendations to reduce input cost by 15-25% and boost crop yield.', 'All farming families cultivating agricultural land across India.', '[\"Aadhaar Card / Voter ID\", \"Land Record (RTC / Survey Number details)\", \"Soil Sample Details Form (Geotagged coordinates, previous crop grown, and irrigation type)\"]', '[\"Step 1: Sample Collection Guidance - Collect grid-based soil samples (V-shaped cut 15 cm deep from 5-10 spots across the field, mix thoroughly, quarter down to 500 grams).\", \"Step 2: Submit Sample to Testing Laboratory - Deliver the labeled 500g soil sample bag to your nearest Raitha Samparka Kendra (RSK), Krishi Vigyan Kendra (KVK), or district mobile soil testing laboratory.\", \"Step 3: Registration on SHC Portal - The agriculture assistant registers your farmer ID, survey number, and sample code on the online portal https://soilhealth.dac.gov.in/.\", \"Step 4: Laboratory Analysis & Prescription Generation - Scientists analyze the 12 soil parameters and generate a customized crop-wise fertilizer prescription table.\", \"Step 5: Card Collection & Implementation - Collect your printed/digital Soil Health Card from the RSK or download it online via OTP, and apply the exact recommended NPK and micronutrient dosage for your upcoming season.\"]', 'Renewed every 2 years', 'https://soilhealth.dac.gov.in/', 'fas fa-vial', NULL, NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(6, 'Krishi Bhagya', 'Flagship Karnataka state water conservation and dryland farming initiative promoting rainwater harvesting through farm ponds (Krishi Honda) and efficient micro-irrigation.', 'state', 'small', 'Up to 80% to 90% financial assistance (subsidy) for constructing farm ponds (Krishi Honda), UV-stabilized polythene lining to prevent seepage, diesel/solar lifting pump sets, and micro-irrigation systems (drip/sprinkler) across 131 rainfed taluks in Karnataka.', 'Small and marginal farmers (80-90% subsidy) and general category farmers (80% subsidy) in rainfed/dryland agricultural zones of Karnataka who own cultivable land and depend primarily on monsoon rainfall.', '[\"Aadhaar Card\", \"Land Ownership Documents (Current year RTC / Pahani and Mutation copy)\", \"Bank Account Passbook (for direct subsidy transfer / vendor payment)\", \"Small/Marginal Farmer Certificate (if claiming 90% subsidy rate)\", \"Caste Certificate (for SC/ST farmers claiming enhanced assistance)\", \"Passport-size Photograph\"]', '[\"Step 1: Visit Raitha Samparka Kendra (RSK) - Approach your Hobli-level Raitha Samparka Kendra or Assistant Director of Agriculture (ADA) office during the application period.\", \"Step 2: Submit Application with Land Profile - Submit the Krishi Bhagya application form along with your RTC, Aadhaar, and proposed farm pond dimensions.\", \"Step 3: Field Pre-Inspection - An Agriculture Officer / Technical Assistant visits your field to verify site feasibility, catchment area, and GPS coordinates for the pond.\", \"Step 4: Sanction Order & Pond Construction - Upon receiving the administrative sanction order, excavate the farm pond and install the UV-stabilized polythene lining as per technical specifications.\", \"Step 5: Post-Inspection & Subsidy Release - Department engineers inspect the completed pond, take geotagged verification photos, and release the subsidy directly via DBT or to the authorized equipment vendor.\"]', 'One-time capital infrastructure subsidy', 'https://raitamitra.karnataka.gov.in/', 'fas fa-water', 'Karnataka', NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(7, 'Ganga Kalyana Scheme', 'Karnataka social welfare irrigation project providing 100% financial assistance for drilling free borewells and installing pump sets for small and marginal SC/ST/OBC farmers.', 'state', 'small', '100% financial assistance (up to Rs. 3.50 Lakhs to Rs. 4.00 Lakhs) for drilling free borewells, supply of submersible pump sets, accessories, and complete electrical electrification/solar energization for small and marginal farmers belonging to SC, ST, OBC, and Minority communities who lack perennial irrigation facilities.', 'Small and marginal farmers holding between 1.20 acres to 5.00 acres of dryland in Karnataka. Must belong to SC/ST (via Dr. B.R. Ambedkar/Valmiki Corporations), OBC (via D. Devaraj Urs Corporation), or Minority communities. Must not have an existing borewell or irrigation connection on their land.', '[\"Aadhaar Card\", \"Land Records (RTC / Pahani covering at least 1.20 acres of contiguous land)\", \"Caste and Income Certificate issued by Tahsildar (Annual family income within prescribed limits)\", \"Small/Marginal Farmer Certificate issued by Revenue Authority\", \"Self-declaration / Affidavit confirming no prior borewell on the property\", \"Bank Account Passbook copy\"]', '[\"Step 1: Check Corporation Portal / Notification - Apply online through the respective development corporation portal (https://kmdeve.karnataka.gov.in/ or Seva Sindhu / KDDC) when the annual enrollment window is announced.\", \"Step 2: Document Submission & Screening - Fill out personal, caste, and land holding details and upload scanned copies of your RTC, Caste/Income certificate, and Aadhaar.\", \"Step 3: Taluk Selection Committee Approval - Applications are screened and selected by the Taluk Level Selection Committee headed by the local MLA and District/Taluk Social Welfare Officers.\", \"Step 4: Groundwater Hydro-geological Survey - Geologists from the Mines & Geology Department conduct scientific groundwater point identification on your farmland.\", \"Step 5: Drilling, Electrification & Handover - Approved empanelled contractors drill the borewell, install the submersible pump set, and coordinate with ESCOMs (BESCOM/HESCOM/GESCOM) for power connection and handover to the farmer.\"]', 'One-time complete irrigation asset provision', 'https://kalyanamitra.karnataka.gov.in/', 'fas fa-tint', 'Karnataka', NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(8, 'Raitha Siri', 'Specialized Karnataka state incentive scheme promoting the cultivation and conservation of nutri-cereals and minor millets (Siri Dhanya) among small and marginal farmers.', 'state', 'marginal', 'Direct cash incentive of Rs. 10,000 per hectare (up to a maximum of 2 hectares / Rs. 20,000 per farmer) for cultivating nutri-cereals / minor millets (Foxtail millet, Little millet, Kodo millet, Proso millet, Barnyard millet, and Browntop millet) during the agricultural season.', 'All farmers in Karnataka who cultivate approved minor millets on their agricultural land during the notified Kharif season. Land registration in RTC under millet crop sowing (Siri Dhanya) is mandatory.', '[\"Aadhaar Card\", \"Land Ownership Record (Updated RTC showing millet crop sowing entry under crop details)\", \"Bank Account Passbook linked with Aadhaar (for direct DBT incentive transfer)\", \"Farmer Registration ID on FRUITS Portal (https://fruits.karnataka.gov.in/)\"]', '[\"Step 1: Register on FRUITS Portal - Ensure you have a valid Farmer ID (FID) on Karnataka\'s FRUITS (Farmer Registration and Unified Beneficiary Information System) portal with your exact RTC linked.\", \"Step 2: Sowing & RTC Crop Booking - Sow minor millets on your farmland during the Kharif season and ensure the Village Accountant / Crop Survey team records the millet crop name correctly in your RTC (Column 12 / Crop details).\", \"Step 3: Submit Raitha Siri Application at RSK - Visit your local Raitha Samparka Kendra (RSK) with your FID, RTC copy, and Aadhaar card to apply for the Raitha Siri incentive.\", \"Step 4: Field Verification by Agriculture Department - The Assistant Agriculture Officer (AAO) verifies field cultivation and checks the digital crop survey record.\", \"Step 5: DBT Cash Incentive Disbursement - Upon successful verification, the Rs. 10,000 per hectare financial incentive is credited directly into your Aadhaar-linked bank account.\"]', 'Seasonal incentive per hectare', 'https://raitamitra.karnataka.gov.in/', 'fas fa-seedling', 'Karnataka', NULL, 1, '2026-05-30 08:58:55', '2026-05-30 08:58:55'),
(9, 'Karnataka Farm Mechanization Support', 'State agricultural engineering initiative subsidizing modern farming equipment, tractors, power tillers, and custom hiring center implements to boost farm productivity.', 'state', 'general', 'Up to 50% to 75% financial subsidy on agricultural machinery including tractors, power tillers, rotavators, seed-cum-fertilizer drills, multi-crop threshers, and plant protection sprayers. Additional 10% subsidy bonus for SC/ST farmers.', 'All registered farmers in Karnataka holding agricultural land. Priority given to small/marginal farmers and those who have not availed farm machinery subsidy under the department in the past 5 to 7 years.', '[\"Aadhaar Card\", \"Land Records (RTC / Pahani copy)\", \"FRUITS Portal Farmer ID (FID)\", \"Bank Account Passbook copy\", \"Caste / Category Certificate (for SC/ST/OBC farmers claiming higher subsidy percentages)\", \"Quotation from Department-Empanelled Machinery Manufacturer/Dealer\"]', '[\"Step 1: Select Approved Machinery & Vendor - Choose the required equipment from the official Karnataka Agriculture Department empanelled rate-contract list and obtain a quotation from an authorized dealer.\", \"Step 2: Submit Application via RSK / DBT Portal - Apply online through the Karnataka DBT Portal or submit physical application with quotation and RTC at the local Raitha Samparka Kendra (RSK).\", \"Step 3: Seniority & Approval Sanction (Permit Order) - Applications are processed based on target allocation and seniority. Once approved, the department issues a formal Purchase Permit (Work Order).\", \"Step 4: Purchase & Vendor Billing - Purchase the machinery by paying your farmer contribution share to the dealer within the stipulated validity period (usually 30 days) and obtain the GST invoice with engine/chassis numbers.\", \"Step 5: Physical Verification & Subsidy Settlement - The Agriculture Officer inspects the machinery, records serial numbers and geotagged farmer photo with the implement, and releases the subsidy directly to the vendor or farmer bank account.\"]', 'Annual target-based scheme', 'https://raitamitra.karnataka.gov.in/', 'fas fa-tractor', 'Karnataka', NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(10, 'Bhoochetana', 'Soil health enhancement and yield-gap reduction program providing subsidized micronutrients and soil amendments directly to Karnataka farmers.', 'state', 'general', 'Supply of essential soil amendments and secondary/micronutrients (Gypsum, Zinc Sulphate, Borax, and bio-fertilizers/vermicompost) at 50% subsidized rates directly through Raitha Samparka Kendras (RSKs) to bridge nutrient deficiencies and increase yield by 20-30%.', 'All farmers across Karnataka whose soil test reports or regional soil fertility maps indicate deficiencies in Zinc, Boron, Sulphur, or Organic Carbon.', '[\"Aadhaar Card\", \"FRUITS Farmer ID (FID) / RTC copy\", \"Soil Health Card or RSK Nutrient Recommendation Slip\"]', '[\"Step 1: Check Nutrient Recommendation - Consult your farm\'s Soil Health Card or ask the Agriculture Officer at the local Raitha Samparka Kendra (RSK) about specific soil deficiencies in your Hobli.\", \"Step 2: Visit RSK During Input Distribution Window - Visit the RSK before sowing season (Kharif/Rabi) when subsidized agricultural inputs and micronutrient bags are stocked.\", \"Step 3: Biometric Authentication & Indent Generation - Provide your FRUITS ID and Aadhaar for biometric/OTP verification on the department Point of Sale (PoS) system.\", \"Step 4: Pay 50% Farmer Cost Share - Pay only 50% of the government rate for the prescribed quantity of Gypsum, Zinc Sulphate, and Boron bags.\", \"Step 5: Field Application - Mix the micronutrients with farmyard manure or soil during basal dressing or land preparation as per the technical dosage chart provided by the RSK agronomist.\"]', 'Seasonal input distribution', 'https://raitamitra.karnataka.gov.in/', 'fas fa-leaf', 'Karnataka', NULL, 1, '2026-05-30 08:58:55', '2026-05-30 08:58:55');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'user',
  `is_approved` tinyint(1) NOT NULL DEFAULT 0,
  `state` varchar(100) DEFAULT 'Karnataka',
  `district` varchar(100) DEFAULT NULL,
  `land_size` float DEFAULT NULL,
  `irrigation_type` varchar(100) DEFAULT NULL,
  `profile_photo` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `phone_number` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `is_approved`, `state`, `district`, `land_size`, `irrigation_type`, `profile_photo`, `created_at`, `updated_at`, `phone_number`) VALUES
(1, 'Admin User', 'admin@cropcare.com', '$2b$12$7p8ZVI6OaRyO418CSRw5Q.byIGiBUsSUaz95zzNZXNPIH6CucT7w2', 'admin', 1, 'Karnataka', NULL, NULL, NULL, NULL, '2026-05-30 08:57:06', '2026-06-12 11:53:14', NULL),
(6, 'Thilak Puthanikar', 'thilakvp@gmail.com', '$2b$12$8.ZchuNGo0XhVYyhkO/wp.pcLzWD/X6m6ptMl97IUM6oIY9OsEJOi', 'user', 1, 'Karnataka', 'Bengaluru Urban', 6, 'Rain-fed', NULL, '2026-06-11 15:46:59', '2026-06-12 10:57:21', '9019280220');

--
-- Indexes for dumped tables
--

CREATE TABLE IF NOT EXISTS district_rainfall (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(100) NOT NULL UNIQUE,
    labels_json TEXT NULL,
    rainfall_json TEXT NULL,
    fetched_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_district_rainfall_district (district)
);


CREATE TABLE IF NOT EXISTS ai_usage_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    feature_type VARCHAR(100) NOT NULL,
    input_payload TEXT NULL,
    output_payload TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ai_history_user_feature (user_id, feature_type),
    CONSTRAINT fk_ai_history_user FOREIGN KEY (user_id) REFERENCES users(id)
);

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `ads`
--
ALTER TABLE `ads`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `crop_plans`
--
ALTER TABLE `crop_plans`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_crop_plans_user` (`user_id`);

--
-- Indexes for table `mandi_prices`
--
ALTER TABLE `mandi_prices`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_mandi_crop_market_week` (`crop_name`,`district`,`mandi_name`,`price_date`);

--
-- Indexes for table `schemes`
--
ALTER TABLE `schemes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `ix_users_phone_number` (`phone_number`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `ads`
--
ALTER TABLE `ads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `crop_plans`
--
ALTER TABLE `crop_plans`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `mandi_prices`
--
ALTER TABLE `mandi_prices`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=73;

--
-- AUTO_INCREMENT for table `schemes`
--
ALTER TABLE `schemes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `crop_plans`
--
ALTER TABLE `crop_plans`
  ADD CONSTRAINT `fk_crop_plans_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
