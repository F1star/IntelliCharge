import threading
import time
from typing import Dict, List, Tuple, Any, Optional
from .WaitingQueue import Queue
from .ChargerPile import ChargingPile

class Scheduler:
    def __init__(self, waiting_queue: Queue, charging_piles: Dict[str, ChargingPile]):
        """
        初始化调度器
        :param waiting_queue: 等待队列实例
        :param charging_piles: 充电桩字典
        """
        self.waiting_queue = waiting_queue
        self.charging_piles = charging_piles
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.check_interval = 5  # 检查间隔（秒）

    def start(self) -> None:
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def stop(self) -> None:
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()

    def _scheduler_loop(self) -> None:
        """调度器主循环"""
        while self.running:
            try:
                self._check_and_schedule()
            except Exception as e:
                print(f"调度器错误: {e}")
            time.sleep(self.check_interval)

    def _check_and_schedule(self) -> None:
        """检查并执行调度"""
        # 更新充电桩信息
        for pile in self.charging_piles.values():
            self.waiting_queue.register_charging_pile(pile.get_queue_info())

        # 执行调度
        schedule_result = self.waiting_queue.schedule_vehicles()
        
        # 处理调度结果
        if schedule_result['fast_allocation'] or schedule_result['slow_allocation']:
            print("执行调度:", schedule_result)
            # 更新充电桩状态
            for vehicle, pile in schedule_result['fast_allocation'] + schedule_result['slow_allocation']:
                print(self.charging_piles[pile['pile_id']].join_queue(vehicle['vehicle_info']['car_id']) )