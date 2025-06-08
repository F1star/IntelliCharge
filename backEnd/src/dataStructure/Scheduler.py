import threading
import time
from typing import Dict, List, Tuple, Any, Optional, Callable
from .WaitingQueue import Queue
from .ChargerPile import ChargingPile

class Scheduler:
    def __init__(self, waiting_queue: Queue, charging_piles: Dict[str, ChargingPile], save_bill_func: Optional[Callable] = None):
        """
        初始化调度器
        :param waiting_queue: 等待队列实例
        :param charging_piles: 充电桩字典
        :param save_bill_func: 保存充电详单的函数
        """
        self.waiting_queue = waiting_queue
        self.charging_piles = charging_piles
        self.save_bill_func = save_bill_func
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
                self._check_charging_status()
            except Exception as e:
                print(f"调度器错误: {e}")
            time.sleep(self.check_interval)

    def _check_and_schedule(self) -> None:
        """检查并执行调度"""
        try:
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
                    result = self.charging_piles[pile['pile_id']].join_queue(vehicle['vehicle_info'])
                    if isinstance(result, dict) and 'error' in result:
                        print(f"调度错误: {result['error']}")
                    else:
                        print(f"调度成功: {result}")
        except Exception as e:
            print(f"调度过程发生错误: {str(e)}")
            
    def _check_charging_status(self) -> None:
        """检查所有充电桩的充电状态，如果达到请求充电量则自动断开"""
        try:
            for pile_id, pile in self.charging_piles.items():
                result = pile.check_charging_status()
                if result:
                    if isinstance(result, dict) and 'error' not in result:
                        print(f"充电桩[{pile_id}]自动断开: {result.get('message', '')}")
                        # 处理充电详单
                        if result.get('bill') and self.save_bill_func:
                            self.save_bill_func(result['bill'])
                    else:
                        print(f"充电桩[{pile_id}]自动断开失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"检查充电状态时发生错误: {str(e)}")