CREATE DATABASE IF NOT EXISTS neuron_test;

CREATE TABLE IF NOT EXISTS neuron_test.job (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	title CHAR(32) NOT NULL UNIQUE
);

insert into neuron_test.job (title) values
	('software engineer');

CREATE TABLE IF NOT EXISTS neuron_test.skill (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	title CHAR(32) NOT NULL UNIQUE
);

insert into neuron_test.skill (title) values
	('effective communication');

CREATE TABLE IF NOT EXISTS neuron_test.scenario (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	title CHAR(32),
	body TEXT NOT NULL,
	skill_id INT NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skill(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS neuron_test.content (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	url CHAR(2083) NOT NULL,
	body TEXT NOT NULL,
	skill_id INT NOT NULL,
	scenario_id INT NOT NULL,
	next_thread_id INT,
	FOREIGN KEY (skill_id) REFERENCES skill(id) ON DELETE CASCADE,
	FOREIGN KEY (scenario_id) REFERENCES scenario(id),
	FOREIGN KEY (next_thread_id) REFERENCES content(id),
	helpfulness_score INT
);

CREATE TABLE IF NOT EXISTS neuron_test.user (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email CHAR(32) NOT NULL,
    first_name CHAR(32) NOT NULL,
    last_name CHAR(32) NOT NULL,
      country CHAR(32) NOT NULL,
	joined_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	current_skill_id INT,
	content_id INT,
	job_id INT,
	organization CHAR(32) DEFAULT '',
	onboarded BOOL DEFAULT 0,
	FOREIGN KEY (current_skill_id) REFERENCES skill(id),
	FOREIGN KEY (content_id) REFERENCES content(id),
	FOREIGN KEY (job_id) REFERENCES job(id)
);

CREATE TABLE IF NOT EXISTS neuron_test.user_response (
    user_id INT NOT NULL PRIMARY KEY,
    message_block_id INT NOT NULL,
    user_response TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
)

CREATE TABLE IF NOT EXISTS neuron_test.message (
    message_id CHAR(32) NOT NULL PRIMARY KEY,
    message_time TIMESTAMP NOT NULL CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    text TEXT NOT NULL
)

INSERT INTO neuron_test.message (message_id, text)
VALUES ('intro_message', 'Hi {first_name} :wave:\n\n:thought_balloon: Imagine you have a dedicated skill coach. All they care about is helping you build competency in the highest value skills :chart_with_upwards_trend: without taking too much time away from your work. They keep track of what skills you’re using, suggest high value skills you may want to consider, and deliver actionable tips to remind you how to get 1% better every day.\n\nWe are that skill coach, and we’re here to help you grow, achieve, and maximize your potential as an engineer! :rocket:\n\n• 3 quick questions about your work \n • 1 short piece of actionable content \n • 1 concrete example curated from the Neuron community\n\nReady to get started? Reply Y or N');

-- Junction table to map users to their courses
CREATE TABLE IF NOT EXISTS neuron_test.user_skill (
	user_id INT REFERENCES user(id),
	skill_id INT REFERENCES skill(id),
	current BOOLEAN NOT NULL DEFAULT FALSE
);
