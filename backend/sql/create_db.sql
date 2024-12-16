-- 創建資料庫
CREATE DATABASE IF NOT EXISTS education_platform;

-- 使用該資料庫
USE education_platform;

-- 創建 users 資料表 (用戶)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 創建 courses 資料表 (課程)
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    video_url VARCHAR(255) DEFAULT NULL, -- 修正：刪除分號
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 創建 video_watch_progress 資料表
CREATE TABLE video_watch_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    last_watched_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 退出觀看的時間
    last_progress INT NOT NULL, -- 用戶觀看影片的進度（秒數）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 創建 assignments 資料表 (作業)
CREATE TABLE assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL, -- 存放 MinIO 文件路徑
    grade FLOAT DEFAULT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 插入初始數據
INSERT INTO users (name, email, password, role) VALUES ('admin', 'admin@example.com', 'adminpassword', 'teacher');
INSERT INTO users (name, email, password, role) VALUES ('user', 'user@example.com', 'userpassword', 'student');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Intro', 'In this video we will introduce LangGraph - a way to more easily create agent runtimes.', 'https://www.youtube.com/watch?v=5h-JBkySK34&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=1');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Agent Executor', 'In this video we will go over how to re-create the canonical LangChain "AgentExecutor" functionality in LangGraph. The benefits of doing it this way are that it will be much easier to modify parts of it to fit your own custom logic.', 'https://www.youtube.com/watch?v=9dXp5q3OFdQ&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=2');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Chat Agent Executor', 'This is a version of an agent executor specifically designed for chat models. It represents state as a list of messages and passes that around. This is a simpler agent runtime for models that support chat messages and function calling.', 'https://www.youtube.com/watch?v=Un-88uJKdiU&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=3');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Human-in-the-Loop', 'This video covers a simple modification to a LangGraph runtime to add a human-in-the-loop component', 'https://www.youtube.com/watch?v=9H4gwJGgvfg&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=4');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Dynamically Returning a Tool Output Directly', 'In this video, we cover how to modify an agent executor to let the LLM determine whether to pass a tool invocation directly as the final output.', 'https://www.youtube.com/watch?v=rabXcLaAlqE&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=5');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Respond in a Specific Format', 'This video covers how to modify an agent runtime to force it to respond in a specific format using function calling.', 'https://www.youtube.com/watch?v=P1aDaYkZzNg&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=6');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Managing Agent Steps', 'This video shows how to modify an agent runtime to have more control over how the intermediate steps of an agent execution run are managed. This is useful for long running agents when there may be many steps.', 'https://www.youtube.com/watch?v=xJ6ipunO16E&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=7');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Force-Calling a Tool', 'In this video we will go over a simple modification you can make the chat agent runtime to force call a tool at the start of the agent execution. This is useful when you want to ensure that a tool is always called first.', 'https://www.youtube.com/watch?v=o5Hw9V5ntxw&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=8');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Multi-Agent Workflows', 'LangGraph makes it easy to construct multi-agent workflows, where each agent is a node, and the edges define how they communicate. In this video we will walk through three examples of multi-agent workflows', 'https://www.youtube.com/watch?v=hvAPnpSfSGo&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=9');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Persistence', 'This video goes over how to add persistence to LangGraph agents. This allows for "memory" in your LangGraph agent applications.', 'https://www.youtube.com/watch?v=YE6A5d8kNp4&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=10');
INSERT INTO courses (title, description, video_url) VALUES ('WebVoyager', 'WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models', 'https://www.youtube.com/watch?v=ylrew7qb8sQ&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=11');
INSERT INTO courses (title, description, video_url) VALUES ('Self-reflective RAG with LangGraph: Self-RAG and CRAG', 'Self-reflection can greatly enhance RAG, enabling correction of poor quality retrieval or generations. Several recent RAG papers focus on this theme, but implementing the ideas can be tricky. Here, we show that LangGraph can be easily used for "flow engineering" of self-reflective RAG pipelines. We provide cookbooks for implementing ideas from two interesting papers, Self-RAG and C-RAG.', 'https://www.youtube.com/watch?v=pbAd8O1Lvm4&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=12');
INSERT INTO courses (title, description, video_url) VALUES ('LangGraph: Planning Agents', 'In this video, we will show you how to build three plan-and-execute style agents using LangGraph, an open-source framework for building stateful, multi-actor AI applications.', 'https://www.youtube.com/watch?v=uRya4zRrRx4&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=13');
INSERT INTO courses (title, description, video_url) VALUES ('Reflection Agents', 'In this video, we will show you how to build three reflection style agents using LangGraph, an open-source framework for building stateful, multi-actor AI applications.', 'https://www.youtube.com/watch?v=v5ymBTXNqtk&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=14');
INSERT INTO courses (title, description, video_url) VALUES ('Building STORM from scratch with LangGraph', 'AI assistants have great potential to automate web research and content generation. A recent work from Shao et al (STORM: Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking) offers a new approach for web research to generate Wikipedia-style articles.', 'https://www.youtube.com/watch?v=1uUORSZwTz4&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=15');
INSERT INTO courses (title, description, video_url) VALUES ('Build Computing Olympiad Agents with LangGraph', 'In this tutorial, we create Olympiad programming agents using LangGraph, drawing upon the techniques and benchmark dataset introduced in the paper "Can Language Models Solve Olympiad Programming?" by Quan Shi, Michael Tang, Karthik Narasimhan, and Shunyu Yao.', 'https://www.youtube.com/watch?v=UqYzzjTmKj8&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=16');
INSERT INTO courses (title, description, video_url) VALUES ('Build a Customer Support Bot | LangGraph', 'In this tutorial, we create a travel assistant chatbot using LangGraph, demonstrating reusable techniques applicable to building any customer support chatbot or AI system that uses tools, supports many user journeys, or requires a high degree of control.', 'https://www.youtube.com/watch?v=b3XsvoFWp4c&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=17');
INSERT INTO courses (title, description, video_url) VALUES ('Build a MemGPT Discord Agent in LangGraph Cloud', 'In this tutorial, we create a MemGPT-inspired Discord agent using LangGraph Cloud, enabling chatbots to remember user interactions across conversations for a more personalized experience.', 'https://www.youtube.com/watch?v=ORAecR4hXsQ&list=PLfaIDFEXuae16n2TWUkKq5PgJ0w6Pkwtg&index=18');
--INSERT INTO courses (title, description, video_url) VALUES ('', '', '');


