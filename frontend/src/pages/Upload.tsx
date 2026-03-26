import React, { useState, useRef, useCallback } from 'react';
import TopBar from '../components/TopBar';
import './Upload.css';

type Stage = 'idle' | 'uploading' | 'analyzing' | 'done' | 'error';

// Mock spectrogram data — 200 time bins × 4 freq bands, with apnea events highlighted
const generateSpectrogramData = () => {
  const bins = 200;
  const data: { time: number; value: number; isApnea: boolean }[][] = [];
  // Apnea windows: [30-50], [80-100], [140-165]
  const apneaWindows = [[30, 50], [80, 100], [140, 165]];
  const isApnea = (t: number) => apneaWindows.some(([a, b]) => t >= a && t <= b);

  for (let f = 0; f < 6; f++) {
    const row = [];
    for (let t = 0; t < bins; t++) {
      const apnea = isApnea(t);
      const base = apnea ? 0.1 + Math.random() * 0.15 : 0.4 + Math.random() * 0.5;
      row.push({ time: t, value: base, isApnea: apnea });
    }
    data.push(row);
  }
  return data;
};

const FREQ_LABELS = ['0-100Hz', '100-200Hz', '200-400Hz', '400-800Hz', '800-1.6kHz', '1.6k-3.2kHz'];

const UploadPage: React.FC = () => {
  const [stage, setStage] = useState<Stage>('idle');
  const [fileName, setFileName] = useState('');
  const [fileSize, setFileSize] = useState('');
  const [progress, setProgress] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const [spectrogramData] = useState(generateSpectrogramData);
  const [analysisResult] = useState({
    ahi: 22.5,
    duration: '7h 32min',
    apneaEvents: 18,
    longestApnea: '68s',
    avgSpo2: 93.4,
    minSpo2: 87,
    severity: '中度',
    recommendation: '建议进行持续气道正压通气(CPAP)治疗，并尽快复诊。'
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    if (!file.name.match(/\.(wav|mp3|flac|ogg|m4a)$/i)) {
      alert('请上传音频文件（WAV / MP3 / FLAC / OGG / M4A）');
      return;
    }
    setFileName(file.name);
    setFileSize((file.size / (1024 * 1024)).toFixed(2) + ' MB');
    setStage('uploading');
    setProgress(0);

    // Simulate upload progress
    let p = 0;
    const uploadTimer = setInterval(() => {
      p += Math.random() * 15;
      if (p >= 100) {
        p = 100;
        clearInterval(uploadTimer);
        setProgress(100);
        setTimeout(() => {
          setStage('analyzing');
          let ap = 0;
          const analyzeTimer = setInterval(() => {
            ap += Math.random() * 8;
            if (ap >= 100) {
              ap = 100;
              clearInterval(analyzeTimer);
              setProgress(100);
              setTimeout(() => setStage('done'), 300);
            }
            setProgress(Math.min(ap, 100));
          }, 200);
        }, 500);
      }
      setProgress(Math.min(p, 100));
    }, 150);
  }, []);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleReset = () => {
    setStage('idle');
    setFileName('');
    setFileSize('');
    setProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div>
      <TopBar
        title="睡眠呼吸检测"
        subtitle="上传睡眠音频，AI 智能分析呼吸阻塞事件"
      />

      <div className="upload-layout">
        {/* Left: Upload Panel */}
        <div className="upload-panel">
          <div className="card">
            <div className="card-title"><span>🎙️</span> 上传音频文件</div>

            {stage === 'idle' && (
              <div
                className={`drop-zone ${dragOver ? 'drop-zone--active' : ''}`}
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="drop-icon">🎵</div>
                <div className="drop-title">拖拽文件到此处，或点击选择</div>
                <div className="drop-hint">支持格式：WAV · MP3 · FLAC · OGG · M4A<br />建议文件大小不超过 500MB</div>
                <button className="btn btn-primary">选择文件</button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".wav,.mp3,.flac,.ogg,.m4a"
                  style={{ display: 'none' }}
                  onChange={e => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
                />
              </div>
            )}

            {(stage === 'uploading' || stage === 'analyzing') && (
              <div className="progress-panel">
                <div className="file-info">
                  <span className="file-icon">🎵</span>
                  <div>
                    <div className="file-name">{fileName}</div>
                    <div className="file-size">{fileSize}</div>
                  </div>
                </div>
                <div className="progress-label">
                  {stage === 'uploading' ? '📤 正在上传...' : '🤖 AI 模型分析中...'}
                </div>
                <div className="progress-bar-wrap">
                  <div className="progress-bar" style={{ width: `${progress.toFixed(0)}%` }} />
                </div>
                <div className="progress-pct">{progress.toFixed(0)}%</div>
                {stage === 'analyzing' && (
                  <div className="analyzing-steps">
                    <div className="step step--done">✅ 音频预处理</div>
                    <div className={`step ${progress > 30 ? 'step--done' : 'step--active'}`}>
                      {progress > 30 ? '✅' : '⏳'} 频谱特征提取
                    </div>
                    <div className={`step ${progress > 60 ? 'step--done' : progress > 30 ? 'step--active' : ''}`}>
                      {progress > 60 ? '✅' : '⏳'} 呼吸阻塞事件检测
                    </div>
                    <div className={`step ${progress > 90 ? 'step--done' : progress > 60 ? 'step--active' : ''}`}>
                      {progress > 90 ? '✅' : '⏳'} 生成检测报告
                    </div>
                  </div>
                )}
              </div>
            )}

            {stage === 'done' && (
              <div className="done-panel">
                <div className="done-icon">✅</div>
                <div className="done-title">分析完成</div>
                <div className="done-file">{fileName} · {fileSize}</div>
                <button className="btn btn-outline" onClick={handleReset}>重新上传</button>
              </div>
            )}
          </div>

          {/* Patient Info Form */}
          <div className="card">
            <div className="card-title"><span>👤</span> 患者信息</div>
            <div className="form-grid">
              <div className="form-group">
                <label>姓名</label>
                <input type="text" placeholder="请输入患者姓名" defaultValue="张三" />
              </div>
              <div className="form-group">
                <label>性别</label>
                <select defaultValue="male">
                  <option value="male">男</option>
                  <option value="female">女</option>
                </select>
              </div>
              <div className="form-group">
                <label>年龄</label>
                <input type="number" placeholder="请输入年龄" defaultValue="45" />
              </div>
              <div className="form-group">
                <label>BMI</label>
                <input type="number" placeholder="如：26.5" defaultValue="27.2" />
              </div>
              <div className="form-group form-group--full">
                <label>既往病史</label>
                <input type="text" placeholder="如：高血压、糖尿病等" defaultValue="高血压" />
              </div>
              <div className="form-group">
                <label>录制日期</label>
                <input type="date" defaultValue="2026-03-25" />
              </div>
              <div className="form-group">
                <label>录制时长</label>
                <input type="text" placeholder="如：7h 30min" defaultValue="7h 32min" />
              </div>
            </div>
          </div>
        </div>

        {/* Right: Results Panel */}
        <div className="results-panel">
          {/* Spectrogram */}
          <div className="card">
            <div className="card-title">
              <span>📊</span> 睡眠呼吸频谱图
              {stage === 'done' && (
                <span className="spectrogram-legend">
                  <span className="legend-dot legend-dot--normal" /> 正常呼吸&nbsp;&nbsp;
                  <span className="legend-dot legend-dot--apnea"  /> 呼吸阻塞事件
                </span>
              )}
            </div>
            {stage !== 'done' ? (
              <div className="spectrogram-placeholder">
                <div className="placeholder-icon">📊</div>
                <div className="placeholder-text">
                  {stage === 'idle' ? '上传音频后将在此处显示频谱图' : '正在生成频谱图...'}
                </div>
              </div>
            ) : (
              <div className="spectrogram-container">
                <div className="spectrogram-y-labels">
                  {FREQ_LABELS.slice().reverse().map(l => (
                    <div key={l} className="y-label">{l}</div>
                  ))}
                </div>
                <div className="spectrogram-canvas-wrap">
                  <svg
                    className="spectrogram-svg"
                    viewBox={`0 0 200 60`}
                    preserveAspectRatio="none"
                  >
                    {spectrogramData.slice().reverse().map((row, fi) =>
                      row.map((cell, ti) => (
                        <rect
                          key={`${fi}-${ti}`}
                          x={ti}
                          y={fi * 10}
                          width={1}
                          height={10}
                          fill={
                            cell.isApnea
                              ? `rgba(229,62,62,${0.4 + cell.value * 0.6})`
                              : `rgba(43,108,176,${0.1 + cell.value * 0.9})`
                          }
                        />
                      ))
                    )}
                  </svg>
                  <div className="apnea-markers">
                    <div className="apnea-marker" style={{ left: '15%', width: '10%' }}>
                      <div className="apnea-marker-label">阻塞事件1</div>
                    </div>
                    <div className="apnea-marker" style={{ left: '40%', width: '10%' }}>
                      <div className="apnea-marker-label">阻塞事件2</div>
                    </div>
                    <div className="apnea-marker" style={{ left: '70%', width: '12.5%' }}>
                      <div className="apnea-marker-label">阻塞事件3</div>
                    </div>
                  </div>
                  <div className="spectrogram-x-labels">
                    <span>0</span><span>1h</span><span>2h</span><span>3h</span>
                    <span>4h</span><span>5h</span><span>6h</span><span>7h</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Analysis Result */}
          {stage === 'done' && (
            <>
              <div className="card">
                <div className="card-title"><span>📈</span> 分析结果摘要</div>
                <div className="result-grid">
                  <div className="result-item result-item--highlight">
                    <div className="result-value result-value--big">{analysisResult.ahi}</div>
                    <div className="result-key">AHI 指数（次/小时）</div>
                    <span className={`badge badge-warning`}>{analysisResult.severity}睡眠呼吸暂停</span>
                  </div>
                  <div className="result-item">
                    <div className="result-value">{analysisResult.apneaEvents}</div>
                    <div className="result-key">呼吸阻塞事件次数</div>
                  </div>
                  <div className="result-item">
                    <div className="result-value">{analysisResult.longestApnea}</div>
                    <div className="result-key">最长阻塞时间</div>
                  </div>
                  <div className="result-item">
                    <div className="result-value">{analysisResult.avgSpo2}%</div>
                    <div className="result-key">平均血氧饱和度</div>
                  </div>
                  <div className="result-item">
                    <div className="result-value result-value--danger">{analysisResult.minSpo2}%</div>
                    <div className="result-key">最低血氧饱和度</div>
                  </div>
                  <div className="result-item">
                    <div className="result-value">{analysisResult.duration}</div>
                    <div className="result-key">总监测时长</div>
                  </div>
                </div>
              </div>

              <div className="card recommendation-card">
                <div className="card-title"><span>💊</span> 医生建议</div>
                <div className="recommendation">
                  <span className="rec-icon">⚕️</span>
                  <p>{analysisResult.recommendation}</p>
                </div>
                <div className="action-btns">
                  <button className="btn btn-primary">📄 生成检测报告</button>
                  <button className="btn btn-accent">📤 导出 PDF</button>
                  <button className="btn btn-outline">📁 保存至病历</button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
