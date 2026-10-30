# GitHub 公开发布

用户于 2026-10-27 明确要求将麻将美术发布到 `luhailong-go` 账号下的公开库。目标仓库为 [luhailong-go/majiang-image](https://github.com/luhailong-go/majiang-image)，分支为 `main`。以该仓库实际远端回执为发布成功依据；本地准备完成不代表上传完成。

## 文件范围

首次发布以 `exports/full-game-package-files.json` 中已验收的完整游戏美术文件集为基线，补充最终包校验、独立复核、本说明与 Git 配置。v3 正式美术为 292 项主 PNG；此前270项保持像素不变，新增22项运行素材，原生来源、提示词、主参考、派生记录、接入文档和必要重建脚本一并保留。

`work/` 默认忽略，只将验收包明确包含的必要来源记录和重建脚本按精确清单加入 Git。在制的 `prototypes/`、缓存、账号凭据、`.env` 与本地发布临时文件不在发布范围。清单见 `exports/git-publication-files.json`。

## 下载和接续

在 GitHub 仓库点击 **Code → Download ZIP** 下载当前全部发布文件，或执行：

```powershell
git clone https://github.com/luhailong-go/majiang-image.git
```

解压或 clone 后打开根 `index.html` 浏览素材；实际游戏接入见 `docs/FULL_GAME_INTEGRATION.md`。当前图片文件均可由普通 Git 保存，不使用 LFS 指针。

本地最新离线包 `exports/yunjian-queshe-complete-art-v4.zip` 不重复放入 Git。旧v2包按最新素材保留规则处理，来源与历史校验文字保留。仓库自带的 Download ZIP 包含对应资源文件；原离线包校验报告的 SHA-256 针对本地交付包，不是 GitHub 自动生成的 ZIP。`exports/full-game-package-files.json` 及旧检查报告是当时交付快照，公开说明改动另由 Git 发布清单记录，不倒改历史来源。

## 最新状态规则

`main` 只保留一个无父提交，表示本次已核验文件树。后续更新先核对远端实际版本，再准备替换的无父提交，并以明确旧版本约束更新；不累积历史提交、额外标签或备份分支。上传失败不改写其他账户仓库，不覆盖未协调的远端更新。

本项目独立于原 `image` 仓库。本次授权只针对麻将项目，不改变原仓库的唯一上传者和固定批次分工。2026-10-26 的“仅本地／未上传”字段是历史交付事实，当前公开发布状态以实际 GitHub 仓库和本地发布回执为准。


## 当前统一交付 v4

当前游戏名为《云间雀社》，293项正式主PNG包含Logo。当前总清单为exports/game-art-with-brand-manifest.json，完整包、组成树、品牌与文档统一核验；旧版本报告仅作历史证据。当前发布文件集见exports/git-publication-files.json，实际Push及匿名下载以最新发布回执为准。
