// ===== 型定義 =====

type Gender = "男性" | "女性" | "その他";

type Character = {
  name: string;
  nameReading: string;
  gender: Gender;
  age: number;
  occupation: string;
  relation: string;
  impression: string;
  aribai: string;
  imagePath: string | null;
};

// ===== 容疑者データ =====

export const suspects: Character[] = [
  {
    name: "橘 蓮",
    nameReading: "たちばな れん",
    gender: "男性",
    age: 29,
    occupation: "フリーランス Webデザイナー",
    relation: "2年前に別れた元彼氏",
    impression:
      "温厚で口数が少なく、一見して害のなさそうな男。別れた後も「友人として」連絡を取り続けていると聞いて安心していたが、複数のアカウントで澪のSNSを監視していたと知り背筋が凍った。感情を表に出さない分、何をため込んでいるのかまるで読めない。",
    aribai: "前日の朝から発見されるまでアリバイは存在しない",
    imagePath: "characters/ren.png",
  },
  {
    name: "早川 奈々",
    nameReading: "はやかわ なな",
    gender: "女性",
    age: 24,
    occupation: "ネイリスト（個人サロン勤務）",
    relation: "幼馴染・10年以上の親友",
    impression:
      "いつも明るくて澪の一番の理解者だと思っていた。でも私と澪が付き合い始めてから、笑顔の裏に何か冷たいものを感じるようになった。「澪はあたしだけのもの」──そんな言葉が彼女の口から出た瞬間、友情と執着の境界線が完全に消えていた。",
    aribai: "犯行時刻の1時間前から発見まで彼氏の家にいたことがわかっている。",
    imagePath: "characters/nana.png",
  },
  {
    name: "朝倉 賢二",
    nameReading: "あさくら けんじ",
    gender: "男性",
    age: 52,
    occupation: "中堅製造業 部長",
    relation: "澪の父親",
    impression:
      "初めて挨拶した日から、品定めするような目線が外れなかった。娘思いの父親を演じているが、澪の交友関係から就職先まで全部コントロールしてきた人物だとあとから知った。澪が「父に絶対知られたくない秘密」を持っていたことが、今となっては恐ろしく思える。",
    aribai: "前日の夜から発見されるまで自宅にいたと妻が証言している。",
    imagePath: "characters/kenji.png",
  },
  {
    name: "三島 恭介",
    nameReading: "みしま きょうすけ",
    gender: "男性",
    age: 31,
    occupation: "ITスタートアップ 営業マネージャー",
    relation: "直属の上司",
    impression:
      "有能で話しやすく、最初は「いい上司だ」と思っていた。でも私の存在を知った途端、澪との距離を急に置き始めた変化が引っかかる。都合が悪くなったら人を切り捨てるタイプだと澪から聞いていた。あの爽やかな笑顔の裏に、どれだけの計算があるのか分からない。",
    aribai:
      "犯行時刻の4時間前から朝まで、会社の同僚と飲み会に参加していたことがわかっている",
    imagePath: "characters/mishima.png",
  },
];

// // ===== UI =====

// const suspectAccents = ["#dc2626", "#d97706", "#7c3aed", "#0891b2"];

// const genderColor: Record<Gender, string> = {
//   "男性": "#3b82f6",
//   "女性": "#ec4899",
//   "その他": "#8b5cf6",
// };

// const PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Crect width='80' height='80' fill='%231e293b'/%3E%3Ccircle cx='40' cy='30' r='16' fill='%2334495e'/%3E%3Cellipse cx='40' cy='70' rx='26' ry='20' fill='%2334495e'/%3E%3C/svg%3E";

// export default function App() {
//   const [selected, setSelected] = useState<Character | null>(null);

//   return (
//     <div style={{ fontFamily: "'Helvetica Neue', sans-serif", minHeight: "100vh", background: "#0f172a", padding: "2rem" }}>
//       <div style={{ textAlign: "center", marginBottom: "2rem" }}>
//         <p style={{ color: "#ef4444", fontSize: "0.75rem", letterSpacing: "0.2em", fontWeight: 700, margin: "0 0 0.4rem" }}>
//           ── 容疑者ファイル ──
//         </p>
//         <h1 style={{ color: "#f1f5f9", fontSize: "1.6rem", margin: "0 0 0.4rem" }}>SUSPECTS</h1>
//         <p style={{ color: "#475569", fontSize: "0.8rem", margin: 0 }}>
//           彼女を殺した犯人は、この中にいる。
//         </p>
//       </div>

//       <div style={{ display: "flex", gap: "1.25rem", justifyContent: "center", flexWrap: "wrap" }}>
//         {suspects.map((s, i) => {
//           const accent = suspectAccents[i];
//           const isOpen = selected === s;

//           return (
//             <div
//               key={s.name}
//               onClick={() => setSelected(isOpen ? null : s)}
//               style={{
//                 background: "#1e293b",
//                 borderRadius: "0.75rem",
//                 boxShadow: isOpen
//                   ? `0 0 0 2px ${accent}, 0 8px 32px rgba(0,0,0,0.4)`
//                   : "0 2px 16px rgba(0,0,0,0.3)",
//                 padding: "1.25rem",
//                 width: "220px",
//                 cursor: "pointer",
//                 transition: "all 0.2s",
//                 borderLeft: `4px solid ${accent}`,
//               }}
//             >
//               <div style={{ display: "flex", justifyContent: "center", marginBottom: "0.875rem" }}>
//                 <img
//                   src={s.imagePath ?? PLACEHOLDER}
//                   alt={s.name}
//                   style={{
//                     width: "72px", height: "72px",
//                     borderRadius: "50%",
//                     objectFit: "cover",
//                     border: `2px solid ${accent}`,
//                     background: "#0f172a",
//                   }}
//                 />
//               </div>

//               <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginBottom: "0.6rem" }}>
//                 <span style={{
//                   background: accent + "30", color: accent,
//                   borderRadius: "0.3rem", padding: "0.15rem 0.5rem",
//                   fontSize: "0.68rem", fontWeight: 700,
//                 }}>
//                   容疑者 {String(i + 1).padStart(2, "0")}
//                 </span>
//                 <span style={{
//                   background: genderColor[s.gender] + "25", color: genderColor[s.gender],
//                   borderRadius: "0.3rem", padding: "0.15rem 0.5rem",
//                   fontSize: "0.68rem", fontWeight: 600,
//                 }}>
//                   {s.gender}
//                 </span>
//               </div>

//               <h2 style={{ margin: "0 0 0.1rem", fontSize: "1.05rem", color: "#f1f5f9", fontWeight: 700 }}>
//                 {s.name}
//               </h2>
//               <p style={{ margin: "0 0 0.1rem", color: "#94a3b8", fontSize: "0.72rem" }}>
//                 {s.nameReading}
//               </p>
//               <p style={{ margin: "0 0 0.5rem", color: "#64748b", fontSize: "0.75rem" }}>
//                 {s.age}歳 / {s.occupation}
//               </p>
//               <p style={{ margin: 0, color: accent, fontSize: "0.72rem", fontWeight: 600 }}>
//                 {s.relation}
//               </p>

//               {isOpen && (
//                 <div style={{
//                   marginTop: "1rem",
//                   paddingTop: "0.875rem",
//                   borderTop: "1px solid #334155",
//                 }}>
//                   <p style={{ margin: "0 0 0.3rem", fontSize: "0.68rem", color: "#64748b", fontWeight: 700, letterSpacing: "0.08em" }}>
//                     自分から見た印象
//                   </p>
//                   <p style={{ margin: 0, fontSize: "0.79rem", color: "#cbd5e1", lineHeight: 1.75 }}>
//                     {s.impression}
//                   </p>
//                 </div>
//               )}
//             </div>
//           );
//         })}
//       </div>

//       <p style={{ textAlign: "center", color: "#334155", fontSize: "0.72rem", marginTop: "2rem" }}>
//         カードをクリックして詳細を表示
//       </p>
//     </div>
//   );
// }
