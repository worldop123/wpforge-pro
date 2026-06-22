/**
 * WPForge Theme - Funnel Dashboard JavaScript
 *
 * 电商漏斗数据面板前端逻辑
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

(function($) {
    'use strict';

    var WPForgeFunnelDashboard = {
        /**
         * 配置
         */
        config: {
            apiBase: wpforgeFunnelData.rest_url,
            nonce: wpforgeFunnelData.nonce,
            startDate: null,
            endDate: null,
            funnelView: 'absolute'
        },

        /**
         * 图表实例
         */
        charts: {
            salesTrend: null,
            conversionTrend: null,
            trafficSources: null,
            deviceDistribution: null
        },

        /**
         * 初始化
         */
        init: function() {
            this.setDefaultDates();
            this.bindEvents();
            this.loadAllData();
        },

        /**
         * 设置默认日期
         */
        setDefaultDates: function() {
            var today = new Date();
            var sevenDaysAgo = new Date();
            sevenDaysAgo.setDate(today.getDate() - 7);

            this.config.endDate = this.formatDate(today);
            this.config.startDate = this.formatDate(sevenDaysAgo);

            $('#funnel-start-date').val(this.config.startDate);
            $('#funnel-end-date').val(this.config.endDate);
        },

        /**
         * 格式化日期
         */
        formatDate: function(date) {
            var year = date.getFullYear();
            var month = String(date.getMonth() + 1).padStart(2, '0');
            var day = String(date.getDate()).padStart(2, '0');
            return year + '-' + month + '-' + day;
        },

        /**
         * 绑定事件
         */
        bindEvents: function() {
            var self = this;

            // 日期预设切换
            $('#funnel-date-preset').on('change', function() {
                self.handleDatePresetChange($(this).val());
            });

            // 自定义日期
            $('#funnel-start-date, #funnel-end-date').on('change', function() {
                self.config.startDate = $('#funnel-start-date').val();
                self.config.endDate = $('#funnel-end-date').val();
                self.loadAllData();
            });

            // 刷新按钮
            $('#funnel-refresh').on('click', function() {
                self.loadAllData();
            });

            // 导出按钮
            $('#funnel-export').on('click', function() {
                self.exportData();
            });

            // 漏斗视图切换
            $('.funnel-toggle').on('click', function() {
                $('.funnel-toggle').removeClass('active');
                $(this).addClass('active');
                self.config.funnelView = $(this).data('view');
                self.renderFunnelChart();
            });

            // 热销产品排序
            $('#top-products-order').on('change', function() {
                self.loadTopProducts($(this).val());
            });
        },

        /**
         * 处理日期预设变化
         */
        handleDatePresetChange: function(preset) {
            var today = new Date();
            var startDate = new Date();

            switch(preset) {
                case 'today':
                    startDate = today;
                    break;
                case 'yesterday':
                    startDate.setDate(today.getDate() - 1);
                    today.setDate(today.getDate() - 1);
                    break;
                case '7days':
                    startDate.setDate(today.getDate() - 7);
                    break;
                case '30days':
                    startDate.setDate(today.getDate() - 30);
                    break;
                case '90days':
                    startDate.setDate(today.getDate() - 90);
                    break;
                case 'this_month':
                    startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                    break;
                case 'last_month':
                    startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                    today = new Date(today.getFullYear(), today.getMonth(), 0);
                    break;
                case 'custom':
                    $('.funnel-date-custom').show();
                    return;
            }

            $('.funnel-date-custom').hide();
            this.config.startDate = this.formatDate(startDate);
            this.config.endDate = this.formatDate(today);
            this.loadAllData();
        },

        /**
         * 加载所有数据
         */
        loadAllData: function() {
            this.loadOverview();
            this.loadFunnelData();
            this.loadSalesTrend();
            this.loadConversionTrend();
            this.loadTopProducts('sales');
            this.loadAbandonedProducts();
            this.loadTrafficSources();
            this.loadDeviceDistribution();
            this.loadInsights();
        },

        /**
         * API请求
         */
        apiRequest: function(endpoint, params) {
            var self = this;
            params = params || {};

            return $.ajax({
                url: this.config.apiBase + endpoint,
                method: 'GET',
                data: params,
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('X-WP-Nonce', self.config.nonce);
                }
            });
        },

        /**
         * 加载概览数据
         */
        loadOverview: function() {
            var self = this;

            this.apiRequest('/funnel/overview', {
                start_date: this.config.startDate,
                end_date: this.config.endDate
            }).done(function(response) {
                if (response.success) {
                    self.updateKPICards(response.data, response.comparison);
                }
            });
        },

        /**
         * 更新KPI卡片
         */
        updateKPICards: function(data, comparison) {
            // 访客数
            this.updateKPICard('visitors', data.visitors, comparison.visitors);

            // 加购数
            this.updateKPICard('add-to-cart', data.add_to_cart, comparison.add_to_cart);

            // 结账数
            this.updateKPICard('checkout', data.checkout_starts, comparison.checkout_starts);

            // 购买数
            this.updateKPICard('purchases', data.purchases, comparison.purchases);

            // 销售额
            this.updateKPICard('revenue', this.formatCurrency(data.revenue), comparison.revenue, true);

            // 转化率
            var conversionRate = data.visitors > 0 ? ((data.purchases / data.visitors) * 100).toFixed(2) + '%' : '0%';
            this.updateKPICard('conversion', conversionRate, comparison.conversion_rate, false, true);
        },

        /**
         * 更新单个KPI卡片
         */
        updateKPICard: function(key, value, comparisonData, isCurrency, isPercentage) {
            $('#kpi-' + key).text(value);

            var $changeEl = $('#kpi-' + key + '-change');
            var change = comparisonData ? comparisonData.change : 0;
            var changeValue = Math.abs(change).toFixed(1) + '%';

            $changeEl.removeClass('positive negative neutral');

            if (change > 0) {
                $changeEl.addClass('positive');
                $changeEl.find('.change-arrow').text('↑');
            } else if (change < 0) {
                $changeEl.addClass('negative');
                $changeEl.find('.change-arrow').text('↓');
            } else {
                $changeEl.addClass('neutral');
                $changeEl.find('.change-arrow').text('—');
            }

            $changeEl.find('.change-value').text(changeValue);
        },

        /**
         * 格式化货币
         */
        formatCurrency: function(value) {
            return '¥' + Number(value).toLocaleString('zh-CN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        },

        /**
         * 加载漏斗数据
         */
        loadFunnelData: function() {
            var self = this;

            this.apiRequest('/funnel/data', {
                start_date: this.config.startDate,
                end_date: this.config.endDate
            }).done(function(response) {
                if (response.success) {
                    self.funnelData = response.data;
                    self.renderFunnelChart();
                }
            });
        },

        /**
         * 渲染漏斗图
         */
        renderFunnelChart: function() {
            if (!this.funnelData) return;

            var stages = this.funnelData.stages;
            var maxValue = stages[0].value;
            var $container = $('#funnel-chart');

            $container.empty();

            stages.forEach(function(stage, index) {
                var percentage = maxValue > 0 ? (stage.value / maxValue) * 100 : 0;
                var width = this.config.funnelView === 'percentage' ? percentage + '%' : 
                            Math.max(percentage, 20) + '%';

                var $stage = $('<div>', { class: 'funnel-stage' });
                var $bar = $('<div>', {
                    class: 'funnel-stage-bar',
                    css: {
                        width: width,
                        backgroundColor: stage.color
                    }
                });

                $bar.append($('<span>', { class: 'funnel-stage-name', text: stage.name }));
                $bar.append($('<span>', { class: 'funnel-stage-value', text: stage.value.toLocaleString() }));

                $stage.append($bar);

                // 转化率
                if (index > 0 && stage.conversion_from_prev !== undefined) {
                    var convClass = stage.conversion_from_prev > 50 ? 'positive' : 'negative';
                    $stage.append($('<span>', {
                        class: 'funnel-stage-conversion ' + convClass,
                        text: stage.conversion_from_prev + '% 转化率'
                    }));
                }

                $container.append($stage);
            }.bind(this));
        },

        /**
         * 加载销售趋势
         */
        loadSalesTrend: function() {
            var self = this;

            this.apiRequest('/funnel/sales-trend', {
                start_date: this.config.startDate,
                end_date: this.config.endDate,
                period: 'day'
            }).done(function(response) {
                if (response.success) {
                    self.renderSalesTrendChart(response.data);
                }
            });
        },

        /**
         * 渲染销售趋势图
         */
        renderSalesTrendChart: function(data) {
            var ctx = document.getElementById('sales-trend-chart');
            if (!ctx) return;

            if (this.charts.salesTrend) {
                this.charts.salesTrend.destroy();
            }

            // 简单的Canvas绘制
            var canvas = ctx.getContext('2d');
            var width = ctx.width = ctx.offsetWidth;
            var height = ctx.height = 300;
            var padding = { top: 20, right: 20, bottom: 40, left: 60 };
            var chartWidth = width - padding.left - padding.right;
            var chartHeight = height - padding.top - padding.bottom;

            // 清空画布
            canvas.clearRect(0, 0, width, height);

            if (!data || !data.labels || data.labels.length === 0) {
                canvas.fillStyle = '#999';
                canvas.font = '14px sans-serif';
                canvas.textAlign = 'center';
                canvas.fillText('暂无数据', width / 2, height / 2);
                return;
            }

            var maxRevenue = Math.max.apply(null, data.revenue) || 1;
            var maxOrders = Math.max.apply(null, data.orders) || 1;

            // 绘制网格线
            canvas.strokeStyle = '#f0f0f0';
            canvas.lineWidth = 1;
            for (var i = 0; i <= 5; i++) {
                var y = padding.top + (chartHeight / 5) * i;
                canvas.beginPath();
                canvas.moveTo(padding.left, y);
                canvas.lineTo(width - padding.right, y);
                canvas.stroke();

                // Y轴标签（销售额）
                var value = maxRevenue * (1 - i / 5);
                canvas.fillStyle = '#999';
                canvas.font = '11px sans-serif';
                canvas.textAlign = 'right';
                canvas.fillText('¥' + Math.round(value / 1000) + 'k', padding.left - 8, y + 4);
            }

            // 绘制柱状图（订单数）
            var barWidth = chartWidth / data.labels.length * 0.6;
            var barGap = chartWidth / data.labels.length * 0.4;

            data.orders.forEach(function(order, i) {
                var x = padding.left + (chartWidth / data.labels.length) * i + barGap / 2;
                var barHeight = (order / maxOrders) * chartHeight * 0.5;
                var y = padding.top + chartHeight - barHeight;

                canvas.fillStyle = 'rgba(59, 130, 246, 0.3)';
                canvas.fillRect(x, y, barWidth, barHeight);
            });

            // 绘制折线图（销售额）
            canvas.strokeStyle = '#3b82f6';
            canvas.lineWidth = 2;
            canvas.beginPath();

            data.revenue.forEach(function(revenue, i) {
                var x = padding.left + (chartWidth / data.labels.length) * i + barGap / 2 + barWidth / 2;
                var y = padding.top + chartHeight - (revenue / maxRevenue) * chartHeight;

                if (i === 0) {
                    canvas.moveTo(x, y);
                } else {
                    canvas.lineTo(x, y);
                }
            });
            canvas.stroke();

            // 绘制数据点
            data.revenue.forEach(function(revenue, i) {
                var x = padding.left + (chartWidth / data.labels.length) * i + barGap / 2 + barWidth / 2;
                var y = padding.top + chartHeight - (revenue / maxRevenue) * chartHeight;

                canvas.fillStyle = '#fff';
                canvas.strokeStyle = '#3b82f6';
                canvas.lineWidth = 2;
                canvas.beginPath();
                canvas.arc(x, y, 4, 0, Math.PI * 2);
                canvas.fill();
                canvas.stroke();
            });

            // X轴标签
            canvas.fillStyle = '#666';
            canvas.font = '11px sans-serif';
            canvas.textAlign = 'center';
            data.labels.forEach(function(label, i) {
                var x = padding.left + (chartWidth / data.labels.length) * i + barGap / 2 + barWidth / 2;
                canvas.fillText(label.substring(5), x, height - padding.bottom + 20);
            });

            // 图例
            canvas.fillStyle = '#3b82f6';
            canvas.fillRect(padding.left, 5, 12, 12);
            canvas.fillStyle = '#666';
            canvas.font = '12px sans-serif';
            canvas.textAlign = 'left';
            canvas.fillText('销售额', padding.left + 18, 15);

            canvas.fillStyle = 'rgba(59, 130, 246, 0.3)';
            canvas.fillRect(padding.left + 80, 5, 12, 12);
            canvas.fillStyle = '#666';
            canvas.fillText('订单数', padding.left + 98, 15);
        },

        /**
         * 加载转化率趋势
         */
        loadConversionTrend: function() {
            // 简化版本，使用模拟数据
            var ctx = document.getElementById('conversion-trend-chart');
            if (!ctx) return;

            var canvas = ctx.getContext('2d');
            var width = ctx.width = ctx.offsetWidth;
            var height = ctx.height = 300;
            var padding = { top: 20, right: 20, bottom: 40, left: 50 };
            var chartWidth = width - padding.left - padding.right;
            var chartHeight = height - padding.top - padding.bottom;

            canvas.clearRect(0, 0, width, height);

            // 模拟数据
            var labels = [];
            var data = [];
            var days = 7;

            for (var i = 0; i < days; i++) {
                var date = new Date();
                date.setDate(date.getDate() - (days - 1 - i));
                labels.push((date.getMonth() + 1) + '/' + date.getDate());
                data.push(2 + Math.random() * 2);
            }

            // 网格线
            canvas.strokeStyle = '#f0f0f0';
            canvas.lineWidth = 1;
            for (var j = 0; j <= 5; j++) {
                var y = padding.top + (chartHeight / 5) * j;
                canvas.beginPath();
                canvas.moveTo(padding.left, y);
                canvas.lineTo(width - padding.right, y);
                canvas.stroke();

                canvas.fillStyle = '#999';
                canvas.font = '11px sans-serif';
                canvas.textAlign = 'right';
                canvas.fillText((5 - j) + '%', padding.left - 8, y + 4);
            }

            // 折线
            var colors = ['#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'];
            var lineLabels = ['整体转化率', '浏览→加购', '加购→结账', '结账→购买', '浏览产品率'];

            for (var line = 0; line < 3; line++) {
                canvas.strokeStyle = colors[line];
                canvas.lineWidth = 2;
                canvas.beginPath();

                for (var k = 0; k < days; k++) {
                    var x = padding.left + (chartWidth / (days - 1)) * k;
                    var y = padding.top + chartHeight - ((data[k] + line * 1.5) / 8) * chartHeight;

                    if (k === 0) {
                        canvas.moveTo(x, y);
                    } else {
                        canvas.lineTo(x, y);
                    }
                }
                canvas.stroke();
            }

            // X轴标签
            canvas.fillStyle = '#666';
            canvas.font = '11px sans-serif';
            canvas.textAlign = 'center';
            labels.forEach(function(label, i) {
                var x = padding.left + (chartWidth / (days - 1)) * i;
                canvas.fillText(label, x, height - padding.bottom + 20);
            });

            // 图例
            for (var l = 0; l < 3; l++) {
                canvas.fillStyle = colors[l];
                canvas.fillRect(padding.left + l * 90, 5, 12, 12);
                canvas.fillStyle = '#666';
                canvas.font = '12px sans-serif';
                canvas.textAlign = 'left';
                canvas.fillText(lineLabels[l], padding.left + l * 90 + 18, 15);
            }
        },

        /**
         * 加载热销产品
         */
        loadTopProducts: function(orderBy) {
            var self = this;

            this.apiRequest('/funnel/top-products', {
                start_date: this.config.startDate,
                end_date: this.config.endDate,
                limit: 10,
                order_by: orderBy
            }).done(function(response) {
                if (response.success) {
                    self.renderProductList('#top-products-list', response.data, orderBy);
                }
            });
        },

        /**
         * 加载弃购产品
         */
        loadAbandonedProducts: function() {
            // 简化版本，使用热销产品数据
            this.apiRequest('/funnel/top-products', {
                start_date: this.config.startDate,
                end_date: this.config.endDate,
                limit: 10,
                order_by: 'add_to_cart'
            }).done(function(response) {
                if (response.success) {
                    // 计算弃购率
                    var products = response.data.map(function(p) {
                        p.abandonment_rate = p.add_to_cart > 0 ? 
                            ((p.add_to_cart - p.purchases) / p.add_to_cart * 100).toFixed(1) : 0;
                        return p;
                    }).sort(function(a, b) {
                        return b.abandonment_rate - a.abandonment_rate;
                    });

                    WPForgeFunnelDashboard.renderAbandonedList('#abandoned-products-list', products);
                }
            });
        },

        /**
         * 渲染产品列表
         */
        renderProductList: function(container, products, orderBy) {
            var $container = $(container);
            $container.empty();

            if (!products || products.length === 0) {
                $container.html('<div class="funnel-loading">暂无数据</div>');
                return;
            }

            var maxValue = products.length > 0 ? products[0][orderBy === 'sales' ? 'purchases' : orderBy] : 1;

            products.forEach(function(product) {
                var value = orderBy === 'sales' ? product.purchases : 
                           orderBy === 'revenue' ? product.revenue :
                           orderBy === 'views' ? product.views : product.add_to_cart;

                var displayValue = orderBy === 'revenue' ? '¥' + Number(value).toLocaleString() : value;
                var percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;

                var $item = $('<div>', { class: 'funnel-product-item' });

                var $image = $('<div>', { class: 'funnel-product-image' });
                if (product.image) {
                    $image.append($('<img>', { src: product.image, alt: product.name }));
                } else {
                    $image.append($('<span>', { class: 'dashicons dashicons-products' }));
                }
                $item.append($image);

                var $info = $('<div>', { class: 'funnel-product-info' });
                $info.append($('<div>', { class: 'funnel-product-name', text: product.name }));
                $info.append($('<div>', { class: 'funnel-product-meta' })
                    .append($('<span>', { text: '浏览: ' + product.views }))
                    .append($('<span>', { text: '加购: ' + product.add_to_cart }))
                    .append($('<span>', { text: '购买: ' + product.purchases }))
                );
                $item.append($info);

                $item.append($('<div>', { class: 'funnel-product-bar' })
                    .append($('<div>', { class: 'funnel-product-bar-fill', css: { width: percentage + '%' } }))
                );

                $item.append($('<div>', { class: 'funnel-product-value', text: displayValue }));

                $container.append($item);
            });
        },

        /**
         * 渲染弃购产品列表
         */
        renderAbandonedList: function(container, products) {
            var $container = $(container);
            $container.empty();

            if (!products || products.length === 0) {
                $container.html('<div class="funnel-loading">暂无数据</div>');
                return;
            }

            var maxRate = products.length > 0 ? products[0].abandonment_rate : 1;

            products.forEach(function(product) {
                var percentage = maxRate > 0 ? (product.abandonment_rate / maxRate) * 100 : 0;

                var $item = $('<div>', { class: 'funnel-product-item' });

                var $image = $('<div>', { class: 'funnel-product-image' });
                if (product.image) {
                    $image.append($('<img>', { src: product.image, alt: product.name }));
                } else {
                    $image.append($('<span>', { class: 'dashicons dashicons-products' }));
                }
                $item.append($image);

                var $info = $('<div>', { class: 'funnel-product-info' });
                $info.append($('<div>', { class: 'funnel-product-name', text: product.name }));
                $info.append($('<div>', { class: 'funnel-product-meta' })
                    .append($('<span>', { text: '加购: ' + product.add_to_cart }))
                    .append($('<span>', { text: '购买: ' + product.purchases }))
                );
                $item.append($info);

                $item.append($('<div>', { class: 'funnel-product-bar' })
                    .append($('<div>', { 
                        class: 'funnel-product-bar-fill', 
                        css: { 
                            width: percentage + '%',
                            background: 'linear-gradient(90deg, #f59e0b, #ef4444)'
                        } 
                    }))
                );

                $item.append($('<div>', { 
                    class: 'funnel-product-value', 
                    text: product.abandonment_rate + '%',
                    css: { color: '#ef4444' }
                }));

                $container.append($item);
            });
        },

        /**
         * 加载流量来源
         */
        loadTrafficSources: function() {
            var self = this;

            this.apiRequest('/funnel/traffic-sources', {
                start_date: this.config.startDate,
                end_date: this.config.endDate
            }).done(function(response) {
                if (response.success) {
                    self.renderPieChart('traffic-sources-chart', response.data);
                }
            });
        },

        /**
         * 加载设备分布
         */
        loadDeviceDistribution: function() {
            var self = this;

            this.apiRequest('/funnel/device-distribution', {
                start_date: this.config.startDate,
                end_date: this.config.endDate
            }).done(function(response) {
                if (response.success) {
                    self.renderPieChart('device-distribution-chart', response.data);
                }
            });
        },

        /**
         * 渲染饼图
         */
        renderPieChart: function(canvasId, data) {
            var ctx = document.getElementById(canvasId);
            if (!ctx) return;

            var canvas = ctx.getContext('2d');
            var width = ctx.width = ctx.offsetWidth;
            var height = ctx.height = 300;
            var centerX = width / 2;
            var centerY = height / 2 - 20;
            var radius = Math.min(centerX, centerY) - 30;

            canvas.clearRect(0, 0, width, height);

            if (!data || data.length === 0) {
                canvas.fillStyle = '#999';
                canvas.font = '14px sans-serif';
                canvas.textAlign = 'center';
                canvas.fillText('暂无数据', centerX, centerY);
                return;
            }

            var colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#6b7280'];
            var total = data.reduce(function(sum, item) {
                return sum + (item.visitors || item.value || 0);
            }, 0);

            var startAngle = -Math.PI / 2;

            data.forEach(function(item, i) {
                var value = item.visitors || item.value || 0;
                var sliceAngle = (value / total) * Math.PI * 2;

                canvas.fillStyle = colors[i % colors.length];
                canvas.beginPath();
                canvas.moveTo(centerX, centerY);
                canvas.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
                canvas.closePath();
                canvas.fill();

                startAngle += sliceAngle;
            });

            // 中心圆（环形图效果）
            canvas.fillStyle = '#fff';
            canvas.beginPath();
            canvas.arc(centerX, centerY, radius * 0.6, 0, Math.PI * 2);
            canvas.fill();

            // 中心文字
            canvas.fillStyle = '#1a1a1a';
            canvas.font = 'bold 20px sans-serif';
            canvas.textAlign = 'center';
            canvas.fillText(total.toLocaleString(), centerX, centerY - 5);
            canvas.fillStyle = '#666';
            canvas.font = '12px sans-serif';
            canvas.fillText('总访客', centerX, centerY + 15);

            // 图例
            var legendY = height - 60;
            var legendX = 20;
            var itemsPerRow = 3;

            data.forEach(function(item, i) {
                var row = Math.floor(i / itemsPerRow);
                var col = i % itemsPerRow;
                var x = legendX + col * (width / itemsPerRow);
                var y = legendY + row * 25;

                canvas.fillStyle = colors[i % colors.length];
                canvas.fillRect(x, y, 12, 12);

                canvas.fillStyle = '#666';
                canvas.font = '12px sans-serif';
                canvas.textAlign = 'left';
                var label = item.label || item.name || '未知';
                var percentage = total > 0 ? ((item.visitors || item.value || 0) / total * 100).toFixed(1) : 0;
                canvas.fillText(label + ' ' + percentage + '%', x + 18, y + 10);
            });
        },

        /**
         * 加载AI洞察
         */
        loadInsights: function() {
            var self = this;

            this.apiRequest('/funnel/insights', {
                start_date: this.config.startDate,
                end_date: this.config.endDate
            }).done(function(response) {
                if (response.success) {
                    self.renderInsights(response.data.insights, response.data.summary);
                }
            });
        },

        /**
         * 渲染洞察
         */
        renderInsights: function(insights, summary) {
            // 渲染摘要
            var $summary = $('#insights-summary');
            $summary.empty();

            if (summary.critical > 0) {
                $summary.append($('<div>', { class: 'insight-summary-item critical' })
                    .append($('<span>', { text: '⚠️ ' + summary.critical + ' 严重' }))
                );
            }
            if (summary.high > 0) {
                $summary.append($('<div>', { class: 'insight-summary-item high' })
                    .append($('<span>', { text: '⚡ ' + summary.high + ' 高优先级' }))
                );
            }
            if (summary.medium > 0) {
                $summary.append($('<div>', { class: 'insight-summary-item medium' })
                    .append($('<span>', { text: '💡 ' + summary.medium + ' 建议' }))
                );
            }

            // 渲染洞察列表
            var $list = $('#insights-list');
            $list.empty();

            if (!insights || insights.length === 0) {
                $list.html('<div class="funnel-loading">暂无洞察建议</div>');
                return;
            }

            insights.forEach(function(insight) {
                var $card = $('<div>', { class: 'funnel-insight-card ' + insight.type });

                var $header = $('<div>', { class: 'insight-header' });
                $header.append($('<span>', { class: 'insight-icon', text: insight.icon }));
                $header.append($('<span>', { class: 'insight-title', text: insight.title }));
                $header.append($('<span>', { class: 'insight-priority ' + insight.priority, text: insight.priority }));
                $card.append($header);

                $card.append($('<div>', { class: 'insight-description', text: insight.description }));

                var $footer = $('<div>', { class: 'insight-footer' });
                $footer.append($('<span>', { class: 'insight-data', text: insight.data }));
                $footer.append($('<span>', { class: 'insight-impact', text: insight.impact }));
                $card.append($footer);

                $list.append($card);
            });
        },

        /**
         * 导出数据
         */
        exportData: function() {
            var url = this.config.apiBase + '/funnel/export' +
                      '?start_date=' + this.config.startDate +
                      '&end_date=' + this.config.endDate +
                      '&format=csv';

            // 添加nonce
            url += '&_wpnonce=' + this.config.nonce;

            window.open(url, '_blank');
        }
    };

    // 初始化
    $(document).ready(function() {
        WPForgeFunnelDashboard.init();
    });

})(jQuery);
