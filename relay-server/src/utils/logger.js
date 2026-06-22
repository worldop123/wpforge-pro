/**
 * WPForge Relay Server - 日志工具
 * 
 * 使用winston提供结构化日志
 */

const winston = require('winston');
const config = require('../config');

const logger = winston.createLogger({
  level: config.logging.level,
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 'wpforge-relay' },
  transports: [
    // 控制台输出
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ timestamp, level, message, ...meta }) => {
          const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
          return `${timestamp} [${level}]: ${message} ${metaStr}`;
        })
      )
    }),
    // 文件输出
    new winston.transports.File({
      filename: config.logging.file,
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 14,
    })
  ]
});

// 创建子日志记录器
function createLogger(moduleName) {
  return logger.child({ module: moduleName });
}

// 默认导出 logger 实例本身（index.js 直接 require 后使用 logger.info），
// 同时挂载 createLogger 与 logger 以支持解构导入：
//   const { createLogger } = require('./utils/logger');
//   const { logger } = require('./utils/logger');
module.exports = logger;
module.exports.createLogger = createLogger;
module.exports.logger = logger;
