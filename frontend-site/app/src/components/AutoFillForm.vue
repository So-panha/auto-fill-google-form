<template>
  <div class="fullscreen-viewport">
    <div class="app-interface-container">
      
      <header class="interface-header">
        <div class="header-main-row">
          <div class="title-group">
            <h2>Upload Files</h2>
            <p class="subtitle-meta">Vertical Excel Layout Template Parser & Automated Form Submitter</p>
          </div>
          <button class="close-btn" title="Close Panel">×</button>
        </div>
      </header>
      
      <main class="workspace-grid">
        
        <div 
          class="upload-active-zone"
          :class="{ 'is-dragging': isDragging, 'has-file': fileState.rawFile }"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleFileDrop"
        >
          <div class="active-content">
            <div class="cloud-icon-wrapper">
              <svg class="cloud-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 16V10M12 10L10 12M12 10L14 12" stroke="#34AADC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M19.3442 15.4241C21.0305 14.1352 21.6033 11.8385 20.6728 9.94614C19.7424 8.05374 17.5199 7.00065 15.394 7.42177C14.7334 5.25301 12.7538 3.73715 10.4907 3.665C8.2276 3.59286 6.16641 4.97811 5.38573 7.09503C3.21557 7.43399 1.63731 9.29415 1.62172 11.4939C1.60613 13.6936 3.15651 15.5802 5.32143 15.9734" stroke="#34AADC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            
            <p class="drag-title">Drag files to upload</p>
            <span class="text-or">or</span>
            
            <label for="excelFile" class="browse-btn">Browse Files</label>
            <input 
              id="excelFile"
              type="file" 
              accept=".xlsx, .xls" 
              class="hidden-input"
              @change="handleFileBrowse" 
            />
            
            <div class="constraint-metadata">
              <p>Max file size: <strong>50MB</strong></p>
              <p>Supported file types: <strong>XLSX, XLS</strong></p>
            </div>
          </div>
        </div>
        
        <div class="submittal-status-tracker">
          <h3>Files Status Overview</h3>
          <div v-if="fileState.rawFile" class="file-status-list">
            
            <div class="state-card" :class="operationStatus">
              <div class="state-info-row">
                <div class="file-meta-block">
                  <span class="status-badge-icon"></span>
                  <div class="name-size-wrapper">
                    <span class="state-filename">{{ fileState.fileName }}</span>
                    <span class="state-filesize">{{ fileState.fileSizeFormatted }}</span>
                  </div>
                </div>
                <button class="delete-file-action" @click="clearFileSlot" title="Remove File">×</button>
              </div>
              
              <div class="progress-container">
                <div class="progress-bar-rail">
                  <div class="progress-fill" :style="{ width: submittalProgress + '%' }"></div>
                </div>
                <span class="progress-text-label" v-if="operationStatus === 'error'">File size exceeds the limit</span>
              </div>
            </div>

          </div>
          
          <div v-else class="tracker-empty-state">
            <p>No files uploaded yet. Drop an Excel file on the left to initialize processing layout parameters.</p>
          </div>
        </div>
        
      </main>

      <div v-if="executionReport" class="log-console-container">
        <div class="console-header">
          <span>SYSTEM APPLICATION CONSOLE LOGS</span>
          <button @click="executionReport = null" class="clear-console-btn">Clear</button>
        </div>
        <pre>{{ executionReport }}</pre>
      </div>

      <footer class="interface-footer-actions">
        <div class="parameter-inputs">
          <div class="input-inline-group">
            <label for="formUrl">Form Target URL:</label>
            <input id="formUrl" v-model="config.url" type="text" placeholder="https://docs.google.com/forms/..." />
          </div>
          <div class="input-inline-group compact">
            <label for="submitCount">Sweeps:</label>
            <input id="submitCount" v-model="config.number" type="number" min="1" />
          </div>
        </div>
        
        <button class="execute-btn" :disabled="isSubmitDisabled" @click="initiateAutomatedFlow">
          {{ operationStatus === 'processing' ? 'Processing Sweeps...' : 'Execute Automated Flow' }}
        </button>
      </footer>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

const config = reactive({
  url: 'https://docs.google.com/forms/d/e/1FAIpQLSdH8CLEYRE5JKlOANv3aVSxEdj...',
  number: 10,
});

const fileState = reactive({
  rawFile: null,
  fileName: '',
  fileSizeFormatted: '',
});

const isDragging = ref(false);
const operationStatus = ref('idle'); // idle, processing, success, error
const submittalProgress = ref(0);
const executionReport = ref(null);

const isSubmitDisabled = computed(() => {
  return !fileState.rawFile || !config.url || operationStatus.value === 'processing';
});

const processRawFile = (file) => {
  if (!file) return;
  fileState.rawFile = file;
  fileState.fileName = file.name;
  fileState.fileSizeFormatted = `${(file.size / (1024 * 1024)).toFixed(1)}MB`;
  
  operationStatus.value = 'idle';
  submittalProgress.value = 40; 
};

const handleDragOver = () => { isDragging.value = true; };
const handleDragLeave = () => { isDragging.value = false; };
const handleFileDrop = (e) => {
  isDragging.value = false;
  if (e.dataTransfer.files.length > 0) processRawFile(e.dataTransfer.files[0]);
};
const handleFileBrowse = (e) => {
  if (e.target.files.length > 0) processRawFile(e.target.files[0]);
};
const clearFileSlot = () => {
  fileState.rawFile = null;
  fileState.fileName = '';
  fileState.fileSizeFormatted = '';
  operationStatus.value = 'idle';
  submittalProgress.value = 0;
  executionReport.value = null;
};

const initiateAutomatedFlow = async () => {
  operationStatus.value = 'processing';
  submittalProgress.value = 70;
  executionReport.value = "[SYSTEM INITIALIZATION]: Booting batch sequence hooks...\n";

  const payload = new FormData();
  payload.append('url', config.url);
  payload.append('number', config.number.toString());
  payload.append('file', fileState.rawFile);

  try {
    const response = await fetch('${import.meta.env.VITE_API_BASE_URL}/api/v1/google_form/auto_fill', {
      method: 'POST',
      body: payload
    });
    
    if (!response.ok) throw new Error("Backend pipeline evaluation exception.");
    
    const resData = await response.json();
    operationStatus.value = 'success';
    submittalProgress.value = 100;
    executionReport.value += `[SUCCESS]: All sweeps performed successfully.\nResponse Data Matrix:\n${JSON.stringify(resData, null, 2)}`;
  } catch (err) {
    operationStatus.value = 'error';
    submittalProgress.value = 100;
    executionReport.value += `[CRITICAL FAULT]: Transaction routine halted.\nDetails: ${err.message}`;
  }
};
</script>
<style scoped>
/* --------------------------------------------------------
   Force Perfect Full-Screen Centering Override
   -------------------------------------------------------- */
.fullscreen-viewport {
  position: fixed; /* Bypasses parent block layout rules completely */
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  background: linear-gradient(135deg, #16d1df 0%, #2979ff 100%);
  
  /* Flexbox Centering Layer */
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  z-index: 9999;
}

/* Fixed Dashboard Container Aspect Ratios */
.app-interface-container {
  width: 90vw;
  height: 85vh;
  max-width: 1200px;
  max-height: 800px;
  background: #ffffff;
  border-radius: 24px;
  padding: 2.5rem;
  box-shadow: 0 25px 55px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

/* --------------------------------------------------------
   A. Header Elements
   -------------------------------------------------------- */
.interface-header {
  margin-bottom: 2rem;
  flex-shrink: 0;
  text-align: left; /* Prevents inheritances from centering titles unexpectedly */
}
.header-main-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.title-group h2 {
  font-size: 1.85rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}
.subtitle-meta {
  margin: 0.35rem 0 0 0;
  font-size: 0.9rem;
  color: #888888;
}
.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #bbb;
  cursor: pointer;
  line-height: 0.8;
}

/* --------------------------------------------------------
   B. Horizontal Workspace Split
   -------------------------------------------------------- */
.workspace-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr; 
  gap: 2.5rem;
  align-items: stretch; 
  flex: 1; 
  min-height: 0; 
  margin-bottom: 1.5rem;
}

/* Left Active Drop Box */
.upload-active-zone {
  border: 2px dashed #34aadc;
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  background: #ffffff;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
}
.upload-active-zone.is-dragging {
  border-color: #2979ff;
  background: #f0f6ff;
}
.upload-active-zone.has-file {
  border-color: #00bcd4;
  background: #faffff;
}
.cloud-icon-wrapper {
  margin-bottom: 1rem;
}
.cloud-icon {
  width: 52px;
  height: 52px;
}
.drag-title {
  font-size: 1.25rem;
  color: #222222;
  margin: 0 0 0.25rem 0;
  font-weight: 600;
}
.text-or {
  font-size: 0.95rem;
  color: #999999;
  display: block;
  margin-bottom: 1rem;
}
.browse-btn {
  display: inline-block;
  padding: 0.55rem 1.5rem;
  border: 1px solid #2979ff;
  border-radius: 24px;
  color: #2979ff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}
.browse-btn:hover {
  background: #2979ff;
  color: #ffffff;
}
.hidden-input {
  display: none;
}
.constraint-metadata {
  margin-top: 1.5rem;
  font-size: 0.85rem;
  color: #999999;
  line-height: 1.4;
}
.constraint-metadata p {
  margin: 0.2rem 0;
}

/* Right Status Area */
.submittal-status-tracker {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  text-align: left;
}
.submittal-status-tracker h3 {
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #444444;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}
.tracker-empty-state {
  color: #999999;
  font-size: 0.95rem;
  line-height: 1.6;
  text-align: center;
  border: 1px solid #f0f0f0;
  border-radius: 16px;
  padding: 2rem;
  background: #fafafa;
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
}
.file-status-list {
  flex: 1;
}

/* Status Item Card Block */
.state-card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1.25rem;
  border: 1px solid #eef2f7;
  border-radius: 14px;
  background: #fbfcfe;
}
.state-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.file-meta-block {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Reference status circles setup */
.status-badge-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-block;
  position: relative;
}
.idle .status-badge-icon,
.processing .status-badge-icon {
  border: 2px solid #00bcd4;
}
.idle .status-badge-icon::after,
.processing .status-badge-icon::after {
  content: '';
  position: absolute;
  top: 4px; left: 4px; width: 6px; height: 6px;
  background: #00bcd4; border-radius: 50%;
}
.success .status-badge-icon {
  border: 2px solid #2979ff;
}
.success .status-badge-icon::after {
  content: '✓';
  font-size: 10px; color: #2979ff; font-weight: bold;
  position: absolute; top: -1px; left: 3px;
}
.error .status-badge-icon {
  border: 2px solid #e91e63;
}

.name-size-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: baseline;
}
.state-filename {
  font-size: 1rem;
  font-weight: 600;
  color: #222222;
}
.state-filesize {
  font-size: 0.85rem;
  color: #888888;
}
.delete-file-action {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #ccc;
  cursor: pointer;
  line-height: 1;
}

/* Horizontal Line Progress Bars */
.progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.progress-bar-rail {
  width: 100%;
  height: 5px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}
.idle .progress-fill,
.processing .progress-fill { background: #00bcd4; }
.success .progress-fill { background: #2979ff; }
.error .progress-fill { background: #e91e63; }

/* --------------------------------------------------------
   C. Code Log Console Output Window
   -------------------------------------------------------- */
.log-console-container {
  background: #18191e;
  border-radius: 12px;
  padding: 1rem;
  max-height: 120px;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  flex-shrink: 0;
  text-align: left;
}
.log-console-container pre {
  margin: 0;
  color: #50fa7b;
  font-family: monospace;
  font-size: 0.85rem;
}

/* --------------------------------------------------------
   D. Control Bar Parameters Footer
   -------------------------------------------------------- */
.interface-footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f2f5;
  padding-top: 1.5rem;
  gap: 2rem;
  flex-shrink: 0;
}
.parameter-inputs {
  display: flex;
  gap: 1.5rem;
  flex: 1;
}
.input-inline-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  text-align: left;
}
.input-inline-group.compact {
  max-width: 110px;
}
.input-inline-group label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #555555;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.input-inline-group input {
  padding: 0.65rem 0.85rem;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 0.95rem;
  color: #333333;
}
.execute-btn {
  background: #2979ff;
  color: #ffffff;
  border: none;
  padding: 0.85rem 2rem;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  align-self: flex-end;
  box-shadow: 0 6px 16px rgba(41, 121, 255, 0.25);
  white-space: nowrap;
}
.execute-btn:hover:not(:disabled) {
  background: #1565c0;
}
.execute-btn:disabled {
  background: #e0e0e0;
  color: #a6a6a6;
  box-shadow: none;
  cursor: not-allowed;
}

/* --------------------------------------------------------
   E. Tablet/Mobile Responsive Fallbacks
   -------------------------------------------------------- */
@media (max-width: 850px) {
  .app-interface-container {
    height: 95vh;
    width: 95vw;
    padding: 1.5rem;
    overflow-y: auto; 
  }
  .workspace-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    flex: none;
  }
  .interface-footer-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 1.25rem;
  }
  .parameter-inputs {
    flex-direction: column;
    gap: 1rem;
  }
  .input-inline-group.compact {
    max-width: 100%;
  }
  .execute-btn {
    align-self: stretch;
  }
}
</style>