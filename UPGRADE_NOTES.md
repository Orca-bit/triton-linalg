# Triton-Linalg 升级说明 (Upgrade Notes)

由于 LLVM/MLIR 升级到 v3.6.0，本项目进行了一系列接口适配和重构。以下是主要更改及其背后的原因。

## 1. ConditionallySpeculatable 接口的引入

在新的 MLIR 版本中，为了更精确地控制算子的可推测性（Speculatability），许多 Dialect 转换和优化（如 `move-backward`）现在依赖于 `ConditionallySpeculatable` 接口。

- **原因**：之前的版本中，可推测性可能通过一些隐式的 trait 或不一致的方式处理。通过显式实现 `getSpeculatability()`，我们能够明确告诉编译器哪些 `LinalgExt` 算子在什么条件下是可以安全移动或提前执行的。
- **实现**：我们在 `LinalgExtBase_Op` 基类中引入了该接口，并在 `LinalgExtOps.cpp` 中通过 `DEFINE_GET_SPECULATABILITY` 宏为所有算子统一提供了 `Speculation::Speculatable` 的默认实现。

## 2. Destination Style Op Interface (DPS) 相关更改

`DestinationStyleOpInterface` 是 MLIR 处理缓冲区分配和输出操作的核心接口。

- **原因**：MLIR 官方对 DPS 接口进行了重构，将旧的 `getDpsInputs()` 和 `getDpsInits()` 替换为 `getDpsInputOperands()` 和 `getDpsInitsMutable()`（或 `getDpsInitOperands()`）。
- **影响**：
    - `getDpsInputOperands()` 返回 `OpOperand*` 范围，这比单纯返回 `Value` 提供了更多的上下文信息（如操作数的索引）。
    - `getDpsInitsMutable()` 允许对输出操作数进行就地修改。
- **适配**：我们更新了 `LinalgExtOps.cpp` 中的所有相关调用，并同步更新了 `TableGen` 定义以符合新的接口要求。

## 3. MemoryEffects Stage 的更改

在 `getEffects` 方法中，`SideEffects::EffectInstance` 的构造函数现在要求明确指定 `stage` 参数。

- **更改示例**：
    - `effects.emplace_back(MemoryEffects::Write::get(), 0, false, ...)` -> `effects.emplace_back(MemoryEffects::Write::get(), /*stage=*/1, ...)`
- **原因**：
    - **Stage 概念**：新的 MLIR 内存副作用模型引入了 `stage` 来区分操作的不同阶段。通常，`stage=0` 代表初始状态或读取阶段，`stage=1` 代表结果产生或写入阶段。
    - **ScalarPrintOp**：对于 `ScalarPrintOp`，其 `Write` 副作用（通常表示对外部资源如标准输出的修改）被标记为 `stage=1`，以明确该副作用发生在操作执行之后。
    - **原子操作 (AtomicRMW/CAS)**：在 `LinalgExtOps.cpp` 的原子操作中，我们将读取标记为 `stage=0`，而将最终的写入标记为 `stage=1`。这有助于别名分析和指令调度器更好地理解原子操作内部的读写顺序关系。
    - **一致性**：这符合 LLVM 对复杂指令副作用的精细化建模趋势，允许编译器在保证正确性的前提下进行更激进的优化。

## 4. 其它 API 迁移

- **MemRefType**: `getStridesAndOffset` 从全局函数变更为成员函数，以增强类型安全性。
- **PointerUnion**: 弃用了 `.is<T>()` 和 `.get<T>()`，改为使用全局的 `isa<T>()` 和 `cast<T>()`，这是为了与 LLVM 整体的风格保持一致。
- **GreedyPatternRewrite**: `applyPatternsAndFoldGreedily` 已被 `applyPatternsGreedily` 替代。
