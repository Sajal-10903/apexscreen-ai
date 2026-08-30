/**
 * A radial progress ring whose fill angle and color are computed directly
 * from the score value (0-10). Unlike a purely decorative ring, this is a
 * genuine data-driven visualization: the conic-gradient sweep angle is
 * `(score / 10) * 360deg`, so two different scores always render visibly
 * different rings.
 */
export default function ScoreRing({ score = 0, size = 100, label = '', showValue = true }) {
  const pct = Math.max(0, Math.min(10, Number(score) || 0)) / 10
  const angle = pct * 360
  const color = pct >= 0.7 ? 'var(--accent-green)' : pct >= 0.4 ? 'var(--accent-amber)' : 'var(--accent-red)'
  const track = 'rgba(255,255,255,0.08)'

  const ringStyle = {
    width: size,
    height: size,
    borderRadius: '50%',
    background: `conic-gradient(${color} ${angle}deg, ${track} ${angle}deg)`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    transition: 'background 0.6s ease',
  }

  const innerStyle = {
    width: size - 14,
    height: size - 14,
    borderRadius: '50%',
    background: 'var(--bg-secondary)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <div style={ringStyle} className="animate-fade-in">
        <div style={innerStyle}>
          {showValue && (
            <span className="font-black" style={{ color, fontSize: size * 0.24 }}>
              {Number(score).toFixed(1)}
            </span>
          )}
          <span className="text-[10px] text-[var(--text-muted)] font-medium">/ 10</span>
        </div>
      </div>
      {label && <p className="text-sm text-[var(--text-secondary)] text-center">{label}</p>}
    </div>
  )
}
