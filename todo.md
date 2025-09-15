# 待改进
1. Tool calling 解析略有问题
现在的实现未把历史记录的tool_calls附上，只附了content
附tool_calls可能影响工具调用和解析

2. context_manager 
对于多个用户指令之间，当下的实现是只记录了过往用户指令+最后一步完成结果，以减少上下文。