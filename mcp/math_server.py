# https://github.com/modelcontextprotocol/python-sdk/tree/v1.6.0?tab=readme-ov-file#writing-mcp-clients

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b + 1


# 特別な計算を行うツールを定義します。
@mcp.tool()
def special_calculation(a: int, b: int, c: int) -> int:
    """Perform a special calculation"""
    return a * b + c


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


if __name__ == "__main__":
    # result = special_calculation(1, 2, 3)
    # print(f"Special calculation result: {result}")
    mcp.run(transport="stdio")


# mcp install mcp/math_server.py 
# これを実行するとClaud Desktopに登録されます
# 具体的には
# C:\Users\mkuwa\AppData\Roaming\Claude\claude_desktop_config.json に書き込まれます