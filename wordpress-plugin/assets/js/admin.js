/**
 * WPForge 管理后台脚本
 */

jQuery(document).ready(function($) {
    'use strict';
    
    // 导入来源切换
    $('#import_source').on('change', function() {
        var source = $(this).val();
        
        if (source === 'wpforge') {
            $('#task-id-row').show();
            $('#file-upload-row').hide();
        } else {
            $('#task-id-row').hide();
            $('#file-upload-row').show();
        }
    });
    
    // 开始导入
    $('#start-import-btn').on('click', function(e) {
        e.preventDefault();
        
        var $btn = $(this);
        var $spinner = $('#import-spinner');
        var $progress = $('#import-progress');
        
        // 显示加载状态
        $btn.prop('disabled', true);
        $spinner.addClass('is-active');
        
        // 显示进度区域
        $progress.show();
        
        // 模拟导入进度（实际应该通过AJAX调用后端API）
        simulateImport();
    });
    
    // 模拟导入进度
    function simulateImport() {
        var total = 100;
        var processed = 0;
        var success = 0;
        var failed = 0;
        var skipped = 0;
        
        var interval = setInterval(function() {
            if (processed >= total) {
                clearInterval(interval);
                $('#start-import-btn').prop('disabled', false);
                $('#import-spinner').removeClass('is-active');
                addLog('导入完成！', 'success');
                return;
            }
            
            processed++;
            
            // 随机生成成功/失败/跳过
            var rand = Math.random();
            if (rand < 0.85) {
                success++;
                addLog('成功导入产品 ' + processed, 'success');
            } else if (rand < 0.95) {
                failed++;
                addLog('导入产品 ' + processed + ' 失败', 'error');
            } else {
                skipped++;
                addLog('跳过产品 ' + processed, 'warning');
            }
            
            // 更新进度
            var percent = Math.round((processed / total) * 100);
            $('#import-progress-fill').css('width', percent + '%');
            $('#import-progress-text').text(percent + '%');
            $('#total-products').text(total);
            $('#success-products').text(success);
            $('#failed-products').text(failed);
            $('#skipped-products').text(skipped);
            
        }, 100);
    }
    
    // 添加日志
    function addLog(message, type) {
        var $log = $('#import-log');
        var time = new Date().toLocaleTimeString();
        var $line = $('<div>').addClass('log-' + type).text('[' + time + '] ' + message);
        $log.append($line);
        $log.scrollTop($log[0].scrollHeight);
    }
    
    // 运行SEO审计
    $('#run-seo-audit').on('click', function() {
        var $btn = $(this);
        var $results = $('#seo-audit-results');
        
        $btn.prop('disabled', true);
        $btn.text('分析中...');
        
        // 模拟SEO审计
        setTimeout(function() {
            $results.show();
            
            // 模拟评分
            animateScore('seo-score-value', 85);
            
            // 模拟问题列表
            var issues = [
                { type: 'warning', message: 'Meta描述长度不足，建议增加到150-160字符' },
                { type: 'info', message: '部分图片缺少ALT标签' },
                { type: 'warning', message: 'H1标签数量过多，建议只使用一个' },
                { type: 'error', message: '部分页面加载速度较慢' }
            ];
            
            var $issuesList = $('#seo-issues-list');
            $issuesList.empty();
            issues.forEach(function(issue) {
                $issuesList.append('<li class="' + issue.type + '">' + issue.message + '</li>');
            });
            
            // 模拟建议列表
            var recommendations = [
                '优化页面标题，包含核心关键词',
                '完善Meta描述，提高点击率',
                '为所有图片添加ALT标签',
                '优化页面加载速度，压缩图片',
                '增加内部链接，提升页面权重'
            ];
            
            var $recList = $('#seo-recommendations-list');
            $recList.empty();
            recommendations.forEach(function(rec) {
                $recList.append('<li>💡 ' + rec + '</li>');
            });
            
            $btn.prop('disabled', false);
            $btn.text('重新分析');
        }, 2000);
    });
    
    // 动画评分
    function animateScore(elementId, targetScore) {
        var $element = $('#' + elementId);
        var current = 0;
        var increment = targetScore / 50;
        
        var interval = setInterval(function() {
            current += increment;
            if (current >= targetScore) {
                current = targetScore;
                clearInterval(interval);
            }
            $element.text(Math.round(current));
        }, 30);
    }
    
    // 运行速度测试
    $('#run-speed-test').on('click', function() {
        var $btn = $(this);
        var $results = $('#speed-test-results');
        
        $btn.prop('disabled', true);
        $btn.text('测试中...');
        
        // 模拟速度测试
        setTimeout(function() {
            $results.show();
            
            // 模拟各项评分
            animateScore('performance-score', 78);
            animateScore('accessibility-score', 92);
            animateScore('best-practices-score', 85);
            animateScore('seo-score', 90);
            
            // 模拟Core Web Vitals
            $('#lcp-value').text('2.8s');
            $('#lcp-status').text('需要改进').addClass('status-warning');
            $('#fid-value').text('45ms');
            $('#fid-status').text('良好').addClass('status-ok');
            $('#cls-value').text('0.05');
            $('#cls-status').text('良好').addClass('status-ok');
            
            // 模拟优化建议
            var opportunities = [
                '压缩图片可以节省 245KB (42%)',
                '延迟加载非关键资源可以减少 1.2s',
                '减少未使用的JavaScript可以节省 180KB',
                '启用文本压缩可以节省 65KB',
                '预连接到第三方源可以加快加载速度'
            ];
            
            var $oppList = $('#speed-opportunities-list');
            $oppList.empty();
            opportunities.forEach(function(opp) {
                $oppList.append('<li>⚡ ' + opp + '</li>');
            });
            
            $btn.prop('disabled', false);
            $btn.text('重新测试');
        }, 3000);
    });
    
    // 一键优化
    $('#one-click-optimize').on('click', function() {
        if (!confirm(wpforgeData.strings.confirm)) {
            return;
        }
        
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.text('优化中...');
        
        // 模拟一键优化
        setTimeout(function() {
            alert('优化完成！已启用图片优化、缓存、Gzip压缩等功能。');
            $btn.prop('disabled', false);
            $btn.text('一键优化');
        }, 2000);
    });
    
    // 测试连接
    $('#test-connection').on('click', function() {
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.text('测试中...');
        
        // 模拟连接测试
        setTimeout(function() {
            alert('连接成功！WPForge API连接正常。');
            $btn.prop('disabled', false);
            $btn.text('测试连接');
        }, 1500);
    });
    
    // 批量SEO优化
    $('#start-bulk-seo').on('click', function() {
        if (!confirm(wpforgeData.strings.confirm)) {
            return;
        }
        
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.text('优化中...');
        
        // 模拟批量优化
        setTimeout(function() {
            alert('批量SEO优化完成！');
            $btn.prop('disabled', false);
            $btn.text('开始批量优化');
        }, 3000);
    });
    
});
