# Claude-Code-Python

一个用Python实现的Claude Code版本，具有多Agent系统和模型集成，提供智能代码生成、文件操作、任务路由等功能。

## 特性

- 🤖 **多Agent系统**: 包含LeadAgent、GeneralPurposeAgent、StatuslineSetupAgent、OutputStyleSetupAgent
- 🔧 **工具集成**: 支持文件操作、系统命令、网络搜索、任务管理等13个专业工具
- 🧠 **模型支持**: 主要使用OpenRouter API，支持Kimi-k2模型，内置MockProvider作为备用
- 💬 **交互式CLI**: 提供友好的命令行界面，支持交互式和单次请求模式
- 📝 **上下文管理**: 智能的对话和项目上下文管理，支持上下文持久化
- 🔄 **任务路由**: 自动将任务路由到最合适的Agent，支持循环式Agent执行
- 🛠️ **模块化架构**: 清晰的分层架构，易于扩展和维护

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

# 调试模式
uv run python main.py --debug

# 指定模型
uv run python main.py --model "moonshotai/kimi-k2-0905"

# 查看帮助
uv run python main.py --help
```

### 基本示例

```python
import asyncio
from claude_code import ClaudeCodeSystem, ClaudeCodeConfig

async def main():
    # 创建配置
    config = ClaudeCodeConfig(
        model="moonshotai/kimi-k2-0905",
        debug_mode=True
    )
    
    # 创建系统
    system = ClaudeCodeSystem(config)
    await system.initialize()
    
    # 处理请求
    response = await system.process_request("写一个快速排序算法")
    print(response['response'])
    
    # 清理资源
    await system.shutdown()

asyncio.run(main())
```

## 项目结构

```
claude-code-python/
├── src/claude_code/           # 主要源代码
│   ├── core/                  # 核心模块
│   ├── agents/                # Agent实现
│   ├── models/                # 模型集成
│   ├── tools/                 # 工具实现
│   ├── utils/                 # 工具模块
│   └── cli.py                 # 命令行界面
├── examples/                  # 示例代码
├── tests/                     # 测试目录
├── docs/                      # 文档目录
├── main.py                    # 主入口
└── pyproject.toml            # 项目配置
```

## Agent系统

- **LeadAgent**: 主Agent，协调其他Agent，处理一般任务，可调用所有工具
- **GeneralPurposeAgent**: 通用Agent，处理复杂研究和多步骤任务
- **StatuslineSetupAgent**: 状态行设置Agent，专门处理Claude Code状态行配置
- **OutputStyleSetupAgent**: 输出样式设置Agent，专门处理Claude Code输出样式创建

## 工具系统

### 文件操作工具
- **Read**: 读取文件内容
- **Write**: 写入文件
- **Edit**: 编辑文件
- **LS**: 列出目录内容
- **Glob**: 文件模式匹配
- **Grep**: 文本搜索

### 系统操作工具
- **Bash**: 执行系统命令

### 网络操作工具
- **WebSearch**: 网络搜索
- **WebFetch**: 获取网页内容

### 任务管理工具
- **TodoWrite**: 任务管理
- **Task**: 任务路由到子Agent
- **Exit**: 终止Agent执行循环

## 架构

详细架构说明请查看 [ARCHITECTURE.md](ARCHITECTURE.md)

## 开发

```bash
# 运行测试
uv run python tests/test_architecture.py

# 运行示例
uv run python examples/basic_usage.py

```

## 配置

### 环境变量
- `OPENROUTER_API_KEY`: OpenRouter API密钥
- `CLAUDE_CODE_DEBUG`: 启用调试模式
- `CLAUDE_CODE_LOG_LEVEL`: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `CLAUDE_CODE_LOG_FILE`: 日志文件路径

### 日志配置
```bash
# 设置日志级别
export CLAUDE_CODE_LOG_LEVEL=DEBUG

# 设置日志文件
export CLAUDE_CODE_LOG_FILE=logs/claude_code.log
```

## 技术特性

- **循环式Agent执行**: Agent支持循环执行直到调用Exit工具
- **智能任务路由**: 基于Agent类型的直接任务路由
- **模型抽象**: 统一的模型接口，支持多模型切换
- **上下文管理**: 维护完整的对话历史和项目状态
- **完整日志系统**: 分级日志记录，性能监控，错误跟踪