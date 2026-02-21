"""
image_gen.py の動作確認スクリプト
生成した画像をローカルファイルに保存して結果を表示する
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


async def main():
    from app.routers.image_gen import _generate_image, _check_spec

    prompt = "A cute cartoon cat sitting on a red pillow"
    spec = "猫が描かれていること"
    max_retries = 3

    print(f"プロンプト: {prompt}")
    print(f"仕様: {spec}")
    print(f"最大リトライ: {max_retries}")
    print("-" * 40)

    last_image_bytes = b""
    last_mime_type = "image/png"

    for attempt in range(1, max_retries + 1):
        print(f"\n[試行 {attempt}/{max_retries}] 画像を生成中...")
        last_image_bytes, last_mime_type = await _generate_image(prompt)
        print(f"  生成完了: {last_mime_type}, {len(last_image_bytes):,} bytes")

        print(f"[試行 {attempt}/{max_retries}] 仕様チェック中...")
        passed = await _check_spec(last_image_bytes, last_mime_type, spec)
        print(f"  仕様チェック: {'[合格]' if passed else '[不合格]'}")

        if passed:
            break

    # 拡張子を決定
    ext_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
    ext = ext_map.get(last_mime_type, ".png")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"generated_image{ext}")

    # ローカルに保存
    with open(out_path, "wb") as f:
        f.write(last_image_bytes)

    print("\n" + "=" * 40)
    print(f"保存先: {out_path}")
    print(f"試行回数: {attempt}")
    print(f"仕様合格: {'はい' if passed else 'いいえ（最終画像を保存）'}")

    # Windows でファイルを自動的に開く
    os.startfile(out_path)


if __name__ == "__main__":
    asyncio.run(main())
