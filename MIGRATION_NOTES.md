# 🔄 Migration Notes - OpenZeppelin v5.0

## 已完成的 OpenZeppelin v5.0 遷移

本專案使用 **OpenZeppelin Contracts v5.0**，相比 v4.x 有重大變更。以下是已完成的遷移：

### ✅ 1. 移除 Counters 庫

**v4.x (舊):**
```solidity
import "@openzeppelin/contracts/utils/Counters.sol";

using Counters for Counters.Counter;
Counters.Counter private _tokenIdCounter;

_tokenIdCounter.increment();
uint256 newTokenId = _tokenIdCounter.current();
```

**v5.0 (新):**
```solidity
uint256 private _tokenIdCounter;

uint256 newTokenId = ++_tokenIdCounter;
```

### ✅ 2. Hook 系統重構

**v4.x (舊):**
```solidity
function _afterTokenTransfer(
    address from,
    address to,
    uint256 tokenId,
    uint256 batchSize
) internal virtual override {
    super._afterTokenTransfer(from, to, tokenId, batchSize);
    // custom logic
}
```

**v5.0 (新):**
```solidity
function _update(
    address to,
    uint256 tokenId,
    address auth
) internal virtual override returns (address) {
    address from = super._update(to, tokenId, auth);
    // custom logic
    return from;
}
```

### 📋 變更摘要

| 變更項目 | v4.x | v5.0 | 狀態 |
|---------|------|------|------|
| Counter | `Counters.sol` | `uint256 counter` | ✅ 完成 |
| Transfer Hook | `_afterTokenTransfer` | `_update` | ✅ 完成 |
| Mint/Burn Hook | `_beforeTokenTransfer` | `_update` | ✅ 完成 |

### 🔗 相關資源

- [OpenZeppelin v5.0 Migration Guide](https://docs.openzeppelin.com/contracts/5.x/upgrades#v5.0)
- [Breaking Changes](https://github.com/OpenZeppelin/openzeppelin-contracts/releases/tag/v5.0.0)

### ✨ 受影響的合約

- ✅ `AgentIdentityRegistry.sol` - 已更新
- ✅ `ReputationRegistry.sol` - 無需更改
- ✅ `ValidationRegistry.sol` - 無需更改

### 🧪 下一步

1. 編譯合約: `cd apps/contracts && pnpm compile`
2. 運行測試: `pnpm test`
3. 部署到本地: `pnpm deploy:local`

---

**遷移日期**: 2025-11-05
**OpenZeppelin Version**: 5.0.1

