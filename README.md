# Claude-Code-Python

一个用Python实现的Claude Code版本，具有多Agent系统和Kimi-k2集成。

## 特性

- 🤖 **多Agent系统**: 包含主Agent、代码Agent、工具Agent、调试Agent、测试Agent和文档Agent
- 🔧 **工具集成**: 支持文件操作、Git操作、终端命令、网络搜索等
- 🧠 **模型支持**: 主要使用Kimi-k2，支持OpenAI作为备用
- 💬 **交互式CLI**: 提供友好的命令行界面
- 📝 **上下文管理**: 智能的对话和项目上下文管理
- 🔄 **任务路由**: 自动将任务路由到最合适的Agent

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd claude-code-python

# 使用uv安装依赖
uv sync

# 设置环境变量
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

### 使用

```bash
# 交互式模式
uv run python main.py

# 单次请求
uv run python main.py --request "帮我写一个Python函数计算斐波那契数列"

# 查看帮助
uv run python main.py --help
```

### 基本示例

```python
import asyncio
from claude_code import ClaudeCodeController, ClaudeCodeConfig

async def main():
    # 创建控制器
    controller = ClaudeCodeController(ClaudeCodeConfig())
    
    # 处理请求
    response = await controller.process_request("写一个快速排序算法")
    print(response['response'])

asyncio.run(main())
```

## 架构

详细架构说明请查看 [ARCHITECTURE.md](ARCHITECTURE.md)

## Agent系统

- **主Agent**: 协调其他Agent，处理一般任务
- **代码Agent**: 代码生成、分析、重构
- **工具Agent**: 工具执行和系统操作
- **调试Agent**: 错误分析和问题解决
- **测试Agent**: 测试生成和质量保证
- **文档Agent**: 文档生成和解释

## 开发

```bash
# 运行测试
uv run pytest

# 运行示例
uv run python examples/basic_usage.py

# 代码格式化
uv run black src/
```