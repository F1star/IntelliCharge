# IntelliCharge 测试指南

本文档介绍如何运行 IntelliCharge 系统的测试并解读测试报告。

## 测试框架

IntelliCharge 使用以下测试框架和工具：

- **unittest**: Python 标准库中的单元测试框架
- **pytest**: 更强大的测试框架，支持更丰富的断言和报告生成
- **coverage**: 代码覆盖率分析工具
- **pytest-html**: 生成 HTML 格式的测试报告

## 测试结构

测试文件位于 `tests` 目录下，包括：

- `test_charging_pile.py`: 测试充电桩功能
- `test_waiting_queue.py`: 测试等候区队列功能
- `test_scheduler.py`: 测试调度器功能
- `test_integration.py`: 系统集成测试
- `test_requirements.py`: 系统需求测试

## 运行测试

### 安装依赖

首先，确保已安装所需的测试工具：

```bash
pip install pytest pytest-html coverage
```

### 方法一：使用脚本运行测试

我们提供了便捷的脚本来运行所有测试并生成报告：

- Windows 用户：运行 `run_tests.bat`
- Linux/Mac 用户：运行 `run_tests.sh` (需要先执行 `chmod +x run_tests.sh`)

### 方法二：手动运行测试

#### 使用 unittest 运行测试

```bash
python -m unittest discover -s tests
```

#### 使用 pytest 运行测试并生成 HTML 报告

```bash
pytest tests -v --html=test_report.html
```

#### 生成代码覆盖率报告

```bash
coverage run -m pytest tests
coverage report -m
coverage html
```

## 测试报告说明

### HTML 测试报告

运行测试后，会在项目根目录生成 `test_report.html` 文件。此报告包含：

- 测试总结：通过/失败的测试数量
- 测试详情：每个测试用例的执行结果
- 测试环境信息：Python 版本、操作系统等

### 代码覆盖率报告

代码覆盖率报告位于 `htmlcov/index.html`，提供以下信息：

- 总体覆盖率：整个项目的代码覆盖率
- 文件覆盖率：每个文件的代码覆盖率
- 行覆盖率：具体到每一行代码是否被测试覆盖

## 测试用例说明

### 充电桩测试 (test_charging_pile.py)

测试充电桩的基本功能，包括初始化、连接/断开车辆、队列管理、故障处理等。

### 等候区队列测试 (test_waiting_queue.py)

测试等候区队列的功能，包括添加/移除车辆、查找车辆、获取队列状态、调度车辆等。

### 调度器测试 (test_scheduler.py)

测试调度器的功能，包括初始化、添加/移除车辆、调度策略、故障处理等。

### 集成测试 (test_integration.py)

测试系统各组件协同工作的情况，包括完整充电流程、修改充电请求、充电桩故障恢复等。

### 需求测试 (test_requirements.py)

验证系统是否满足需求规格说明中的各项要求，包括充电桩数量、充电功率、等候区容量等。

## 常见问题

1. **测试失败如何处理？**
   - 检查错误信息，定位问题所在
   - 检查相关代码是否有修改
   - 确认测试环境是否正确设置

2. **如何添加新的测试用例？**
   - 在相应的测试文件中添加新的测试方法
   - 测试方法名应以 `test_` 开头
   - 使用 `self.assert*` 方法验证结果

3. **如何提高代码覆盖率？**
   - 查看覆盖率报告中未覆盖的代码行
   - 添加针对这些代码的测试用例
   - 注意边界条件和异常情况的测试 