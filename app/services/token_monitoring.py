#!/usr/bin/env python3
"""
SmartCompute Token Monitoring Service
Advanced token tracking, cost estimation, and optimization
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics

from prometheus_client import Counter, Histogram, Gauge, Info


class TokenProvider(Enum):
    """AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic" 
    GOOGLE = "google"
    AZURE = "azure"
    CUSTOM = "custom"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class TokenUsage:
    """Token usage data structure"""
    timestamp: str
    provider: str
    model: str
    operation_type: str
    tokens_input: int
    tokens_output: int
    tokens_total: int
    cost_usd: float
    duration_seconds: float
    user_id: str = "default"
    project_id: str = "default"
    priority: str = "normal"


@dataclass
class BudgetAlert:
    """Budget alert data structure"""
    timestamp: str
    alert_type: str  # "warning", "critical", "exhausted"
    current_usage_usd: float
    budget_limit_usd: float
    percentage_used: float
    project_id: str
    estimated_time_to_limit: Optional[str]


class TokenMonitoringService:
    """
    Advanced token monitoring service with cost tracking, budgets, and optimization
    """
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Data storage
        self.usage_history: List[TokenUsage] = []
        self.budget_alerts: List[BudgetAlert] = []
        self.max_history_size = 10000
        
        # Budgets (USD)
        self.project_budgets: Dict[str, float] = {"default": 1000.0}
        self.daily_budgets: Dict[str, float] = {"default": 100.0}
        
        # Cost models (USD per 1K tokens)
        self.token_costs = {
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
            }
        }
        
        # ML estimation models
        self.estimation_accuracy = {"default": 0.85}  # 85% accuracy initially
        self.learning_data: Dict[str, List[float]] = {}
        
        # Callbacks
        self.alert_callbacks: List[Callable] = []
        self.optimization_callbacks: List[Callable] = []
        
        # Initialize Prometheus metrics
        self._init_metrics()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _init_metrics(self):
        """Initialize Prometheus metrics for token monitoring"""
        
        # Token usage metrics
        self.tokens_consumed_total = Counter(
            'smartcompute_tokens_consumed_total',
            'Total tokens consumed',
            ['provider', 'model', 'operation_type', 'user_id', 'project_id']
        )
        
        self.tokens_cost_usd_total = Counter(
            'smartcompute_tokens_cost_usd_total',
            'Total token costs in USD',
            ['provider', 'model', 'user_id', 'project_id']
        )
        
        self.tokens_per_operation = Histogram(
            'smartcompute_tokens_per_operation',
            'Tokens consumed per operation',
            ['provider', 'model', 'operation_type'],
            buckets=[10, 50, 100, 500, 1000, 2000, 5000, 10000, 20000]
        )
        
        self.token_operation_duration = Histogram(
            'smartcompute_token_operation_duration_seconds',
            'Token operation duration in seconds',
            ['provider', 'model', 'operation_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        # Budget metrics
        self.budget_utilization = Gauge(
            'smartcompute_budget_utilization_percent',
            'Budget utilization percentage',
            ['project_id', 'budget_type']
        )
        
        self.budget_remaining_usd = Gauge(
            'smartcompute_budget_remaining_usd',
            'Remaining budget in USD',
            ['project_id', 'budget_type']
        )
        
        # Optimization metrics
        self.tokens_saved_optimization = Counter(
            'smartcompute_tokens_saved_optimization_total',
            'Tokens saved through optimization',
            ['optimization_type', 'project_id']
        )
        
        self.cost_savings_usd = Counter(
            'smartcompute_cost_savings_usd_total',
            'Cost savings in USD through optimization',
            ['optimization_type', 'project_id']
        )
        
        # Estimation accuracy
        self.estimation_accuracy_score = Gauge(
            'smartcompute_estimation_accuracy_score',
            'Token estimation accuracy score',
            ['provider', 'model']
        )
    
    async def start_monitoring(self) -> bool:
        """Start token monitoring service"""
        if self.is_monitoring:
            return False
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("SmartCompute token monitoring service started")
        return True
    
    async def stop_monitoring(self) -> bool:
        """Stop token monitoring service"""
        if not self.is_monitoring:
            return True
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        self.logger.info("SmartCompute token monitoring service stopped")
        return True
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await self._perform_budget_checks()
                await self._update_metrics()
                await self._optimize_if_needed()
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in token monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    def track_token_usage(self, provider: str, model: str, operation_type: str,
                         tokens_input: int, tokens_output: int, duration: float,
                         user_id: str = "default", project_id: str = "default",
                         priority: str = "normal", actual_cost: Optional[float] = None):
        """Track token usage with cost calculation"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tokens_total = tokens_input + tokens_output
        
        # Calculate cost
        if actual_cost is not None:
            cost_usd = actual_cost
            # Update estimation accuracy
            estimated_cost = self._estimate_cost(provider, model, tokens_input, tokens_output)
            if estimated_cost > 0:
                accuracy = min(1.0, cost_usd / estimated_cost) if estimated_cost >= cost_usd else min(1.0, estimated_cost / cost_usd)
                self._update_estimation_accuracy(provider, model, accuracy)
        else:
            cost_usd = self._estimate_cost(provider, model, tokens_input, tokens_output)
        
        # Create usage record
        usage = TokenUsage(
            timestamp=timestamp,
            provider=provider,
            model=model,
            operation_type=operation_type,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            cost_usd=cost_usd,
            duration_seconds=duration,
            user_id=user_id,
            project_id=project_id,
            priority=priority
        )
        
        # Store in history
        self.usage_history.append(usage)
        if len(self.usage_history) > self.max_history_size:
            self.usage_history = self.usage_history[-self.max_history_size:]
        
        # Update Prometheus metrics
        self._update_prometheus_metrics(usage)
        
        self.logger.info(f"Tracked token usage: {tokens_total} tokens, ${cost_usd:.4f}")
        
        return usage
    
    def _estimate_cost(self, provider: str, model: str, tokens_input: int, tokens_output: int) -> float:
        """Estimate cost based on token usage"""
        
        # Try to get exact pricing
        if provider in self.token_costs and model in self.token_costs[provider]:
            pricing = self.token_costs[provider][model]
            input_cost = (tokens_input / 1000) * pricing["input"]
            output_cost = (tokens_output / 1000) * pricing["output"]
            return input_cost + output_cost
        
        # Fallback estimation based on historical data
        avg_cost_per_token = self._get_average_cost_per_token(provider, model)
        return (tokens_input + tokens_output) * avg_cost_per_token
    
    def _get_average_cost_per_token(self, provider: str, model: str) -> float:
        """Get average cost per token from historical data"""
        
        relevant_usage = [
            usage for usage in self.usage_history
            if usage.provider == provider and usage.model == model
            and usage.tokens_total > 0
        ]
        
        if not relevant_usage:
            # Default fallback pricing
            return 0.002  # $0.002 per token (conservative estimate)
        
        costs_per_token = [usage.cost_usd / usage.tokens_total for usage in relevant_usage]
        return statistics.mean(costs_per_token)
    
    def _update_estimation_accuracy(self, provider: str, model: str, accuracy: float):
        """Update estimation accuracy for ML learning"""
        
        key = f"{provider}_{model}"
        if key not in self.learning_data:
            self.learning_data[key] = []
        
        self.learning_data[key].append(accuracy)
        
        # Keep only recent data (last 100 samples)
        if len(self.learning_data[key]) > 100:
            self.learning_data[key] = self.learning_data[key][-100:]
        
        # Update accuracy score
        self.estimation_accuracy[key] = statistics.mean(self.learning_data[key])
        
        # Update Prometheus metric
        self.estimation_accuracy_score.labels(
            provider=provider, 
            model=model
        ).set(self.estimation_accuracy[key])
    
    def _update_prometheus_metrics(self, usage: TokenUsage):
        """Update Prometheus metrics with usage data"""
        
        labels = {
            'provider': usage.provider,
            'model': usage.model,
            'operation_type': usage.operation_type,
            'user_id': usage.user_id,
            'project_id': usage.project_id
        }
        
        # Token consumption
        self.tokens_consumed_total.labels(**labels).inc(usage.tokens_total)
        
        # Cost tracking
        cost_labels = {k: v for k, v in labels.items() if k != 'operation_type'}
        self.tokens_cost_usd_total.labels(**cost_labels).inc(usage.cost_usd)
        
        # Operation metrics
        op_labels = {k: v for k, v in labels.items() if k not in ['user_id', 'project_id']}
        self.tokens_per_operation.labels(**op_labels).observe(usage.tokens_total)
        self.token_operation_duration.labels(**op_labels).observe(usage.duration_seconds)
    
    async def _perform_budget_checks(self):
        """Check budget limits and generate alerts"""
        
        for project_id in self.project_budgets:
            # Daily budget check
            daily_usage = self._get_daily_usage(project_id)
            daily_budget = self.daily_budgets.get(project_id, 100.0)
            daily_percentage = (daily_usage / daily_budget) * 100
            
            # Monthly budget check
            monthly_usage = self._get_monthly_usage(project_id)
            monthly_budget = self.project_budgets[project_id]
            monthly_percentage = (monthly_usage / monthly_budget) * 100
            
            # Update Prometheus metrics
            self.budget_utilization.labels(
                project_id=project_id, 
                budget_type="daily"
            ).set(daily_percentage)
            
            self.budget_utilization.labels(
                project_id=project_id, 
                budget_type="monthly"
            ).set(monthly_percentage)
            
            self.budget_remaining_usd.labels(
                project_id=project_id, 
                budget_type="daily"
            ).set(max(0, daily_budget - daily_usage))
            
            self.budget_remaining_usd.labels(
                project_id=project_id, 
                budget_type="monthly"
            ).set(max(0, monthly_budget - monthly_usage))
            
            # Generate alerts
            await self._check_budget_alerts(project_id, daily_usage, daily_budget, "daily")
            await self._check_budget_alerts(project_id, monthly_usage, monthly_budget, "monthly")
    
    async def _check_budget_alerts(self, project_id: str, usage: float, budget: float, period: str):
        """Check and generate budget alerts"""
        
        percentage = (usage / budget) * 100
        
        if percentage >= 100:
            alert_type = "exhausted"
        elif percentage >= 90:
            alert_type = "critical"
        elif percentage >= 75:
            alert_type = "warning"
        else:
            return  # No alert needed
        
        # Estimate time to limit
        estimated_time = self._estimate_time_to_budget_limit(project_id, usage, budget, period)
        
        alert = BudgetAlert(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            alert_type=alert_type,
            current_usage_usd=usage,
            budget_limit_usd=budget,
            percentage_used=percentage,
            project_id=project_id,
            estimated_time_to_limit=estimated_time
        )
        
        self.budget_alerts.append(alert)
        
        # Limit alert history
        if len(self.budget_alerts) > 1000:
            self.budget_alerts = self.budget_alerts[-1000:]
        
        # Notify callbacks
        await self._notify_alert_callbacks(alert)
        
        self.logger.warning(f"BUDGET ALERT: {alert_type.upper()} - Project {project_id} at {percentage:.1f}% of {period} budget")
    
    def _get_daily_usage(self, project_id: str) -> float:
        """Get today's token usage cost for project"""
        today = datetime.now().date()
        
        daily_usage = [
            usage for usage in self.usage_history
            if usage.project_id == project_id
            and datetime.strptime(usage.timestamp, '%Y-%m-%d %H:%M:%S').date() == today
        ]
        
        return sum(usage.cost_usd for usage in daily_usage)
    
    def _get_monthly_usage(self, project_id: str) -> float:
        """Get this month's token usage cost for project"""
        current_month = datetime.now().replace(day=1).date()
        
        monthly_usage = [
            usage for usage in self.usage_history
            if usage.project_id == project_id
            and datetime.strptime(usage.timestamp, '%Y-%m-%d %H:%M:%S').date() >= current_month
        ]
        
        return sum(usage.cost_usd for usage in monthly_usage)
    
    def _estimate_time_to_budget_limit(self, project_id: str, current_usage: float, 
                                     budget_limit: float, period: str) -> Optional[str]:
        """Estimate time until budget limit is reached"""
        
        if current_usage >= budget_limit:
            return "Budget exceeded"
        
        # Get recent usage trend (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_usage = [
            usage for usage in self.usage_history
            if usage.project_id == project_id
            and datetime.strptime(usage.timestamp, '%Y-%m-%d %H:%M:%S') >= recent_cutoff
        ]
        
        if len(recent_usage) < 2:
            return None
        
        recent_cost = sum(usage.cost_usd for usage in recent_usage)
        hourly_rate = recent_cost / 24  # Average hourly spend
        
        if hourly_rate <= 0:
            return None
        
        remaining_budget = budget_limit - current_usage
        hours_remaining = remaining_budget / hourly_rate
        
        if hours_remaining < 1:
            return f"{int(hours_remaining * 60)} minutes"
        elif hours_remaining < 24:
            return f"{int(hours_remaining)} hours"
        else:
            return f"{int(hours_remaining / 24)} days"
    
    async def _update_metrics(self):
        """Update system metrics"""
        # This could include updating estimation accuracy, performance metrics, etc.
        pass
    
    async def _optimize_if_needed(self):
        """Perform optimization if budget pressure is detected"""
        
        for project_id in self.project_budgets:
            daily_usage = self._get_daily_usage(project_id)
            daily_budget = self.daily_budgets.get(project_id, 100.0)
            
            if daily_usage / daily_budget > 0.8:  # 80% of daily budget used
                await self._trigger_optimization(project_id)
    
    async def _trigger_optimization(self, project_id: str):
        """Trigger optimization strategies"""
        
        optimization_strategies = [
            "switch_to_cheaper_model",
            "reduce_output_tokens",
            "cache_frequent_requests",
            "batch_operations"
        ]
        
        for strategy in optimization_strategies:
            # Notify optimization callbacks
            for callback in self.optimization_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(project_id, strategy)
                    else:
                        callback(project_id, strategy)
                except Exception as e:
                    self.logger.error(f"Error in optimization callback: {e}")
    
    async def _notify_alert_callbacks(self, alert: BudgetAlert):
        """Notify registered alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    # Public API methods
    
    def set_project_budget(self, project_id: str, monthly_budget: float, daily_budget: float):
        """Set budget limits for a project"""
        self.project_budgets[project_id] = monthly_budget
        self.daily_budgets[project_id] = daily_budget
        self.logger.info(f"Budget set for {project_id}: ${daily_budget}/day, ${monthly_budget}/month")
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for budget alerts"""
        self.alert_callbacks.append(callback)
    
    def register_optimization_callback(self, callback: Callable):
        """Register callback for optimization triggers"""
        self.optimization_callbacks.append(callback)
    
    def get_usage_statistics(self, project_id: str = None, days: int = 7) -> Dict[str, Any]:
        """Get token usage statistics"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_usage = [
            usage for usage in self.usage_history
            if (project_id is None or usage.project_id == project_id)
            and datetime.strptime(usage.timestamp, '%Y-%m-%d %H:%M:%S') >= cutoff_date
        ]
        
        if not filtered_usage:
            return {"error": "No usage data available"}
        
        total_tokens = sum(usage.tokens_total for usage in filtered_usage)
        total_cost = sum(usage.cost_usd for usage in filtered_usage)
        
        provider_stats = {}
        for usage in filtered_usage:
            if usage.provider not in provider_stats:
                provider_stats[usage.provider] = {"tokens": 0, "cost": 0, "requests": 0}
            provider_stats[usage.provider]["tokens"] += usage.tokens_total
            provider_stats[usage.provider]["cost"] += usage.cost_usd
            provider_stats[usage.provider]["requests"] += 1
        
        return {
            "period_days": days,
            "project_id": project_id or "all",
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "average_cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0,
            "total_requests": len(filtered_usage),
            "provider_breakdown": provider_stats,
            "daily_average_cost": total_cost / days
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent budget alerts"""
        recent_alerts = self.budget_alerts[-limit:] if self.budget_alerts else []
        return [asdict(alert) for alert in recent_alerts]
    
    def export_usage_data(self, filepath: str, project_id: str = None, days: int = 30):
        """Export usage data to JSON file"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_usage = [
            usage for usage in self.usage_history
            if (project_id is None or usage.project_id == project_id)
            and datetime.strptime(usage.timestamp, '%Y-%m-%d %H:%M:%S') >= cutoff_date
        ]
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'project_id': project_id or 'all',
            'period_days': days,
            'usage_data': [asdict(usage) for usage in filtered_usage],
            'budget_alerts': [asdict(alert) for alert in self.budget_alerts[-100:]],
            'statistics': self.get_usage_statistics(project_id, days)
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            self.logger.info(f"Usage data exported to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export usage data: {e}")
            return False