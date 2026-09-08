CREATE TABLE `audit` (
	`id` text PRIMARY KEY NOT NULL,
	`session` text NOT NULL,
	`position` integer NOT NULL,
	`record` text NOT NULL,
	FOREIGN KEY (`session`) REFERENCES `sessions`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `audit_session_position` ON `audit` (`session`,`position`);--> statement-breakpoint
CREATE TABLE `limits` (
	`id` text PRIMARY KEY NOT NULL,
	`count` integer NOT NULL,
	`expires` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `limits_expiry` ON `limits` (`expires`);--> statement-breakpoint
CREATE TABLE `sessions` (
	`id` text PRIMARY KEY NOT NULL,
	`state` text NOT NULL,
	`revision` integer DEFAULT 0 NOT NULL,
	`expires` integer NOT NULL,
	`last_op` text,
	`last_reply` text
);
--> statement-breakpoint
CREATE INDEX `sessions_expiry` ON `sessions` (`expires`);