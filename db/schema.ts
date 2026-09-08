import { sqliteTable, text, integer, index } from 'drizzle-orm/sqlite-core';
export const sessions = sqliteTable('sessions', {
 id: text('id').primaryKey(), state: text('state').notNull(), revision: integer('revision').notNull().default(0),
 expires: integer('expires').notNull(), lastOp: text('last_op'), lastReply: text('last_reply'),
},t=>[index('sessions_expiry').on(t.expires)]);
export const audit = sqliteTable('audit', {
 id: text('id').primaryKey(), session: text('session').notNull().references(()=>sessions.id,{onDelete:'cascade'}),
 position: integer('position').notNull(), record: text('record').notNull(),
},t=>[index('audit_session_position').on(t.session,t.position)]);
export const limits = sqliteTable('limits', {id:text('id').primaryKey(),count:integer('count').notNull(),expires:integer('expires').notNull()},t=>[index('limits_expiry').on(t.expires)]);
