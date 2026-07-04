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
(1, 'PM-KISAN Samman Nidhi', 'Income support scheme for eligible farmer families through direct benefit transfer.', 'national', 'small', 'Rs. 6,000 per year in three installments.', 'Landholding farmer families, subject to central government exclusions.', '[\"Aadhaar card\", \"Bank account details\", \"Land records\"]', '[\"Visit the PM-KISAN portal or nearest agriculture office.\", \"Submit Aadhaar, bank details, and land ownership records.\", \"Complete beneficiary verification.\", \"Track payment status through the official portal.\"]', 'Ongoing', 'https://pmkisan.gov.in/', 'fas fa-rupee-sign', NULL, NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(2, 'Pradhan Mantri Fasal Bima Yojana', 'Crop insurance support for notified crops against yield losses and localized risks.', 'national', 'general', 'Insurance coverage for crop loss subject to notified crop and season rules.', 'Farmers cultivating notified crops in notified areas.', '[\"Aadhaar card\", \"Bank passbook\", \"Land record or cultivation proof\", \"Sowing details\"]', '[\"Check whether your crop and area are notified for the season.\", \"Apply through the official portal, bank, or Common Service Center.\", \"Submit land and sowing details before the deadline.\", \"Report losses within the prescribed timeline if crop damage occurs.\"]', 'Seasonal enrollment', 'https://pmfby.gov.in/', 'fas fa-shield-alt', NULL, NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(3, 'Soil Health Card Scheme', 'Soil testing program that helps farmers improve nutrient management and crop planning.', 'national', 'general', 'Field-specific soil nutrient recommendations and soil health reporting.', 'Farmers seeking soil testing support through agriculture department channels.', '[\"Land details\", \"Farmer ID proof\", \"Soil sample information\"]', '[\"Contact the local agriculture office or soil testing center.\", \"Submit the soil sample following the recommended method.\", \"Register the sample with land and farmer details.\", \"Collect the soil health report and follow nutrient guidance.\"]', 'Periodic testing support', 'https://soilhealth.dac.gov.in/', 'fas fa-vial', NULL, NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(4, 'Krishi Bhagya', 'Karnataka support program focused on farm ponds and rainwater conservation for dryland farmers.', 'state', 'small', 'Support for water harvesting structures and related conservation components.', 'Eligible Karnataka farmers, especially in rain-fed and dryland areas, subject to state norms.', '[\"Aadhaar card\", \"RTC or land records\", \"Bank account details\", \"Passport-size photo\"]', '[\"Visit the local Raitha Samparka Kendra or Karnataka agriculture office.\", \"Submit land and identity documents for scheme screening.\", \"Complete field verification by department staff.\", \"Receive approval and proceed as per department guidance.\"]', 'State program cycle', 'https://raitamitra.karnataka.gov.in/', 'fas fa-water', 'Karnataka', NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(5, 'Karnataka Farm Mechanization Support', 'State assistance for eligible farmers adopting approved agricultural machinery and equipment.', 'state', 'general', 'Subsidy support on approved implements and mechanization components as per state norms.', 'Eligible farmers in Karnataka applying through the agriculture department process.', '[\"Aadhaar card\", \"Land records\", \"Quotation or invoice\", \"Bank account details\"]', '[\"Review the approved machinery list and subsidy norms.\", \"Apply through the notified Karnataka agriculture portal or office.\", \"Upload or submit land, identity, and equipment documents.\", \"Complete verification and claim processing after approval.\"]', 'Annual or notification-based', 'https://raitamitra.karnataka.gov.in/', 'fas fa-tractor', 'Karnataka', NULL, 1, '2026-05-30 08:57:06', '2026-05-30 08:57:06'),
(6, 'Kisan Credit Card', 'Institutional credit support for crop production, allied activities, and working capital needs.', 'national', 'general', 'Access to short-term agricultural credit through participating banks.', 'Farmers, tenant farmers, sharecroppers, and eligible allied-sector beneficiaries as per bank norms.', '[\"Identity proof\", \"Address proof\", \"Land or cultivation records\", \"Passport-size photo\"]', '[\"Approach a participating bank branch or apply through the official KCC process.\", \"Submit identity, address, and cultivation details.\", \"Complete bank verification and credit assessment.\", \"Receive the sanctioned KCC limit and card access.\"]', 'Renewable credit facility', 'https://www.myscheme.gov.in/schemes/kcc', 'fas fa-credit-card', NULL, NULL, 1, '2026-05-30 08:58:55', '2026-05-30 08:58:55'),
(7, 'Raitha Siri', 'Karnataka support initiative for eligible small and marginal farmers to improve cultivation capacity.', 'state', 'marginal', 'State support targeted at resource-constrained farmers under notified conditions.', 'Eligible small and marginal farmers in Karnataka as notified by the state.', '[\"Aadhaar card\", \"Land records\", \"Income or category proof if applicable\", \"Bank account details\"]', '[\"Check current eligibility guidance with the local agriculture office.\", \"Submit application through the notified Karnataka agriculture channel.\", \"Attach land, identity, and bank details.\", \"Await verification and sanction communication.\"]', 'As per state notification', 'https://raitamitra.karnataka.gov.in/', 'fas fa-seedling', 'Karnataka', NULL, 1, '2026-05-30 08:58:55', '2026-05-30 08:58:55'),
(8, 'Bhoochetana', 'Karnataka soil and productivity improvement program promoting balanced nutrient management and extension support.', 'state', 'general', 'Agronomic support for improving soil fertility and farm productivity.', 'Farmers in Karnataka covered by the notified implementation areas.', '[\"Aadhaar card\", \"Land records\", \"Bank details if subsidy-linked\", \"Crop details\"]', '[\"Visit the local agriculture office or Raitha Samparka Kendra.\", \"Register your land and crop details.\", \"Participate in field guidance or department screening.\", \"Follow the approved package or support channel provided.\"]', 'Season-based implementation', 'https://raitamitra.karnataka.gov.in/', 'fas fa-leaf', 'Karnataka', NULL, 1, '2026-05-30 08:58:55', '2026-05-30 08:58:55');

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

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
