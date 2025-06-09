#!/bin/bash

echo "==================================="
echo "开始运行IntelliCharge系统测试..."
echo "==================================="

# 激活虚拟环境（如果有）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo
echo "1. 运行测试并生成HTML报告..."
pytest tests -v --html=test_report.html

echo
echo "2. 生成代码覆盖率报告..."
coverage run -m pytest tests
coverage report -m
coverage html

echo
echo "==================================="
echo "测试完成！"
echo "- HTML测试报告: test_report.html"
echo "- 代码覆盖率报告: htmlcov/index.html"
echo "===================================" 