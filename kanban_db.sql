-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1:3306
-- Время создания: Май 27 2025 г., 09:15
-- Версия сервера: 8.0.30
-- Версия PHP: 8.0.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `kanban_db`
--

-- --------------------------------------------------------

--
-- Структура таблицы `activity`
--

CREATE TABLE `activity` (
  `id` int NOT NULL,
  `task_id` int NOT NULL,
  `action_type` varchar(50) DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `activity`
--

INSERT INTO `activity` (`id`, `task_id`, `action_type`, `description`, `created_at`) VALUES
(74, 44, 'Создание', 'Задача \"Добавить ассоциацию\" создана', '2025-05-24 14:44:39'),
(78, 44, 'Изменение веса', 'Вес изменён на \"4\"', '2025-05-24 14:46:52'),
(79, 44, 'Изменение статуса', 'Статус изменён с \"В работе\" на \"Открытые\"', '2025-05-24 14:48:04'),
(80, 44, 'Изменение статуса', 'Статус изменён с \"Открытые\" на \"В работе\"', '2025-05-24 14:48:05'),
(81, 44, 'Добавление метки', 'Метка \"Bug\" добавлена', '2025-05-24 14:48:48'),
(82, 44, 'Изменение статуса', 'Статус изменён с \"В работе\" на \"Для тестов\"', '2025-05-24 14:48:57'),
(83, 44, 'Изменение статуса', 'Статус изменён с \"Для тестов\" на \"В тесте\"', '2025-05-24 14:48:58'),
(84, 44, 'Изменение статуса', 'Статус изменён с \"В тесте\" на \"В работе\"', '2025-05-24 14:48:59'),
(85, 44, 'Изменение описание', 'Описание изменено', '2025-05-24 14:51:55'),
(86, 44, 'Изменение описание', 'Описание изменено', '2025-05-24 14:52:03'),
(88, 44, 'Добавление вложения', 'Файл \"Screenshot_2024-05-31_151003.png\" загружен', '2025-05-24 15:41:13'),
(89, 44, 'Добавление вложения', 'Файл \"Screenshot_2024-05-07_002633.png\" загружен', '2025-05-24 15:42:43'),
(90, 44, 'Добавление вложения', 'Файл \"Screenshot_2024-05-21_212425.png\" загружен', '2025-05-24 15:55:41'),
(91, 44, 'Удаление вложения', 'Файл \"Screenshot_2024-05-07_002633.png\" удален', '2025-05-24 16:01:42'),
(92, 44, 'Удаление вложения', 'Файл \"Screenshot_2024-05-21_212551.png\" удален', '2025-05-24 16:01:44'),
(93, 44, 'Удаление вложения', 'Файл \"Screenshot_2024-09-10_221346.png\" удален', '2025-05-24 16:01:46'),
(94, 44, 'Удаление вложения', 'Файл \"Screenshot_2024-05-31_151003.png\" удален', '2025-05-24 16:01:47'),
(95, 1, 'Добавление вложения', 'Файл \"Screenshot_2024-05-07_002633.png\" загружен', '2025-05-24 16:11:50'),
(96, 1, 'Удаление вложения', 'Файл \"Screenshot_2024-05-07_002633.png\" удален', '2025-05-24 16:12:02'),
(97, 44, 'Добавление вложения', 'Файл \"Screenshot_2024-06-26_193045.png\" загружен', '2025-05-24 16:12:54'),
(98, 44, 'Удаление вложения', 'Файл \"Screenshot_2024-06-26_193045.png\" удален', '2025-05-24 16:13:00'),
(99, 44, 'Добавление вложения', 'Файл \"Screenshot_2024-05-31_151003.png\" загружен', '2025-05-24 16:13:34'),
(100, 44, 'Удаление вложения', 'Файл \"Screenshot_2024-05-31_151003.png\" удален', '2025-05-24 16:13:38'),
(101, 44, 'Добавление метки', 'Метка \"to test\" добавлена', '2025-05-24 16:20:32'),
(102, 44, 'Удаление метки', 'Метка \"doing\" удалена', '2025-05-24 16:20:32'),
(103, 44, 'Изменение статуса', 'Статус изменён с \"В работе\" на \"Для тестов\"', '2025-05-24 16:20:42'),
(104, 44, 'Изменение статуса', 'Статус изменён с \"Для тестов\" на \"В работе\"', '2025-05-24 16:20:43'),
(109, 44, 'Изменение статуса', 'Статус изменён с \"В работе\" на \"Открытые\"', '2025-05-24 17:01:53'),
(110, 44, 'Изменение статуса', 'Статус изменён с \"Открытые\" на \"В работе\"', '2025-05-24 17:01:54'),
(111, 50, 'Создание', 'Задача \"Тестовая задача\" создана', '2025-05-24 19:18:39'),
(112, 44, 'Создание', 'Добавлен комментарий', '2025-05-24 19:51:03'),
(113, 50, 'Добавление комментария', 'Добавлен комментарий', '2025-05-24 19:55:32'),
(114, 50, 'Изменение описание', 'Описание изменено', '2025-05-24 19:55:58'),
(115, 50, 'Добавление метки', 'Метка \"Bug\" добавлена', '2025-05-24 19:56:06'),
(116, 51, 'Создание', 'Задача \"Тестовая задача 2\" создана', '2025-05-24 20:02:22'),
(117, 51, 'Добавление метки', 'Метка \"Bug\" добавлена', '2025-05-24 20:28:24');

-- --------------------------------------------------------

--
-- Структура таблицы `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('0fe4ef829728');

-- --------------------------------------------------------

--
-- Структура таблицы `attachment`
--

CREATE TABLE `attachment` (
  `id` int NOT NULL,
  `filename` varchar(255) NOT NULL,
  `data` mediumblob NOT NULL,
  `content_type` varchar(100) NOT NULL,
  `task_id` int NOT NULL,
  `uploaded_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `comment`
--

CREATE TABLE `comment` (
  `id` int NOT NULL,
  `content` text NOT NULL,
  `task_id` int NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `comment`
--

INSERT INTO `comment` (`id`, `content`, `task_id`, `created_at`) VALUES
(4, 'КОММ', 1, '2025-05-24 19:41:39'),
(5, 'комм', 44, '2025-05-24 19:48:19'),
(6, 'фф', 44, '2025-05-24 19:51:03'),
(7, 'Комментарий', 50, '2025-05-24 19:55:32');

-- --------------------------------------------------------

--
-- Структура таблицы `label`
--

CREATE TABLE `label` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` text,
  `color` varchar(20) DEFAULT '#888888'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `label`
--

INSERT INTO `label` (`id`, `name`, `description`, `color`) VALUES
(2, 'Bug', 'Непредвиденные ошибки в задаче', '#ff0000'),
(3, 'To approve', 'Содержимое задачи требует проверки', '#f0ff1f'),
(8, 'doing', 'Задача в работе', '#1f9eff'),
(9, 'to test', 'Задача подготовлена к тестированию', '#00ffee'),
(10, 'testing', 'Задача тестируется', '#aa00ff'),
(12, 'closed', 'Задача закрыта', '#b5b5b5'),
(13, 'open', 'Задача открыта', '#a9ff9e');

-- --------------------------------------------------------

--
-- Структура таблицы `status`
--

CREATE TABLE `status` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `label_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `status`
--

INSERT INTO `status` (`id`, `name`, `label_id`) VALUES
(1, 'Открытые', 13),
(2, 'В работе', 8),
(3, 'Для тестов', 9),
(4, 'В тесте', 10),
(5, 'Закрытые', 12);

-- --------------------------------------------------------

--
-- Структура таблицы `task`
--

CREATE TABLE `task` (
  `id` int NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text,
  `status_id` int NOT NULL,
  `task_order` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `weight` int DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `confidentiality` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `task`
--

INSERT INTO `task` (`id`, `title`, `description`, `status_id`, `task_order`, `created_at`, `updated_at`, `weight`, `due_date`, `confidentiality`) VALUES
(1, 'Заполнение в СИ значение конечного узла-получателя', '### Описание\r\nДля случая отправки НАК после поиска SsoChannel, согласно которому необходимо направить SpecialInfoObject конечному получателю, записать значения из SsoChannel в поля:\r\n\r\n      SpecialInfoObject.FinalUs = SsoChannel.Us\r\n      SpecialInfoObject.FinalCc = SsoChannel.Cc\r\n\r\nЗначения данных полей обновлять при каждом поиске SsoChannel (в том числе при смене канала для корреспондента) для данного SpecialInfoObject.\r\nДля случая отправки ОТК поля:\r\n\r\n      SpecialInfoObject.FinalUs = центральный узел\r\n      SpecialInfoObject.FinalCc = СДПИ (номер 04)\r\n', 1, 0, '2025-05-02 18:50:32', '2025-05-24 14:43:45', 2, NULL, NULL),
(44, 'Добавить ассоциацию', 'Для эдитора', 2, 0, '2025-05-24 14:44:39', '2025-05-24 17:01:54', 4, '2025-05-25', NULL),
(50, 'Тестовая задача', 'Измененное описание задачи', 1, 1, '2025-05-24 19:18:39', '2025-05-24 20:15:11', 10, '2025-05-25', NULL),
(51, 'Тестовая задача 2', '', 1, 2, '2025-05-24 20:02:22', '2025-05-24 20:15:11', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Структура таблицы `task_label`
--

CREATE TABLE `task_label` (
  `task_id` int NOT NULL,
  `label_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `task_label`
--

INSERT INTO `task_label` (`task_id`, `label_id`) VALUES
(44, 2),
(50, 2),
(51, 2),
(44, 8),
(1, 13),
(50, 13),
(51, 13);

-- --------------------------------------------------------

--
-- Структура таблицы `task_link`
--

CREATE TABLE `task_link` (
  `task_id` int NOT NULL,
  `linked_task_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Дамп данных таблицы `task_link`
--

INSERT INTO `task_link` (`task_id`, `linked_task_id`) VALUES
(3, 1),
(5, 1),
(29, 1),
(44, 1),
(1, 44),
(51, 50),
(50, 51);

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `activity`
--
ALTER TABLE `activity`
  ADD PRIMARY KEY (`id`),
  ADD KEY `task_id` (`task_id`);

--
-- Индексы таблицы `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Индексы таблицы `attachment`
--
ALTER TABLE `attachment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `task_id` (`task_id`);

--
-- Индексы таблицы `comment`
--
ALTER TABLE `comment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `task_id` (`task_id`);

--
-- Индексы таблицы `label`
--
ALTER TABLE `label`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Индексы таблицы `status`
--
ALTER TABLE `status`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `label_id` (`label_id`);

--
-- Индексы таблицы `task`
--
ALTER TABLE `task`
  ADD PRIMARY KEY (`id`),
  ADD KEY `status_id` (`status_id`);

--
-- Индексы таблицы `task_label`
--
ALTER TABLE `task_label`
  ADD PRIMARY KEY (`task_id`,`label_id`),
  ADD KEY `label_id` (`label_id`);

--
-- Индексы таблицы `task_link`
--
ALTER TABLE `task_link`
  ADD PRIMARY KEY (`task_id`,`linked_task_id`),
  ADD KEY `linked_task_id` (`linked_task_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `activity`
--
ALTER TABLE `activity`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=118;

--
-- AUTO_INCREMENT для таблицы `attachment`
--
ALTER TABLE `attachment`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT для таблицы `comment`
--
ALTER TABLE `comment`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT для таблицы `label`
--
ALTER TABLE `label`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT для таблицы `status`
--
ALTER TABLE `status`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT для таблицы `task`
--
ALTER TABLE `task`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `activity`
--
ALTER TABLE `activity`
  ADD CONSTRAINT `activity_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`);

--
-- Ограничения внешнего ключа таблицы `attachment`
--
ALTER TABLE `attachment`
  ADD CONSTRAINT `attachment_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `comment`
--
ALTER TABLE `comment`
  ADD CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`);

--
-- Ограничения внешнего ключа таблицы `status`
--
ALTER TABLE `status`
  ADD CONSTRAINT `status_ibfk_1` FOREIGN KEY (`label_id`) REFERENCES `label` (`id`);

--
-- Ограничения внешнего ключа таблицы `task`
--
ALTER TABLE `task`
  ADD CONSTRAINT `task_ibfk_1` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`);

--
-- Ограничения внешнего ключа таблицы `task_label`
--
ALTER TABLE `task_label`
  ADD CONSTRAINT `task_label_ibfk_2` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`),
  ADD CONSTRAINT `task_label_ibfk_3` FOREIGN KEY (`label_id`) REFERENCES `label` (`id`);

--
-- Ограничения внешнего ключа таблицы `task_link`
--
ALTER TABLE `task_link`
  ADD CONSTRAINT `task_link_ibfk_1` FOREIGN KEY (`linked_task_id`) REFERENCES `task` (`id`),
  ADD CONSTRAINT `task_link_ibfk_1_cascade` FOREIGN KEY (`linked_task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
