<template>
  <div class="home">
    <UploadOverlay v-if="isDragover && !banStatus.is_banned" />
    <UploadProgress 
      v-if="uploadingFiles.length > 0" 
      :files="uploadingFiles" 
      @close="uploadingFiles = []"
    />

    <!-- Ban Notice -->
    <div v-if="banStatus.is_banned" class="ban-notice">
      <div class="ban-notice__icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
      </div>
      <div class="ban-notice__content">
        <h3>{{ $t('appeal.banNotice') }}</h3>
        <p class="ban-notice__reason">{{ $t('appeal.banReason', { reason: banStatus.reason || $t('appeal.defaultReason') }) }}</p>
        <p v-if="banStatus.expires_at" class="ban-notice__expires">
          {{ $t('appeal.banExpires', { time: formatBanExpiry(banStatus.expires_at) }) }}
        </p>
        <p v-else class="ban-notice__expires ban-notice__expires--permanent">{{ $t('appeal.banPermanent') }}</p>
        
        <!-- Appeal Section -->
        <div v-if="userStore.isLoggedIn" class="ban-notice__appeal">
          <template v-if="banStatus.existing_appeal">
            <div class="appeal-status">
              <span class="appeal-status__label">{{ $t('appeal.appealStatus') }}：</span>
              <span :class="['appeal-status__value', 'appeal-status__value--' + banStatus.existing_appeal.status]">
                {{ getAppealStatusText(banStatus.existing_appeal.status) }}
              </span>
            </div>
            <p v-if="banStatus.existing_appeal.admin_response" class="appeal-response">
              {{ $t('appeal.adminResponse') }}：{{ banStatus.existing_appeal.admin_response }}
            </p>
          </template>
          <button 
            v-if="banStatus.can_appeal" 
            class="btn btn--appeal" 
            @click="showAppealDialog = true"
          >
            {{ $t('appeal.submitAppeal') }}
          </button>
        </div>
        <p v-else class="ban-notice__login-hint">
          <router-link to="/login">{{ $t('auth.login') }}</router-link> {{ $t('appeal.loginToAppeal') }}
        </p>
      </div>
    </div>
    
    <div class="home__card">
      <!-- Left Panel -->
      <div class="home__left">
        <div class="brand">
          <img v-if="currentLogo" :src="currentLogo" :alt="siteStore.siteName()" class="brand__logo" />
          <h1 v-else class="brand__name">{{ siteStore.siteName() }}</h1>
          <p class="brand__tagline">{{ siteStore.siteSlogan() }}</p>
        </div>
        
        <div class="features">
          <div 
            v-for="(feature, index) in siteStore.homeFeatures()" 
            :key="index" 
            class="feature"
          >
            <svg class="feature__icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            {{ siteStore.getLocalizedText(feature, $i18n.locale) }}
          </div>
        </div>
        
        <div class="divider"></div>
        
        <table class="compare">
          <thead>
            <tr>
              <th></th>
              <th>{{ siteStore.getLocalizedText(siteStore.homeTableCols().col_guest, $i18n.locale) || $t('home.guest') }}</th>
              <th>{{ siteStore.getLocalizedText(siteStore.homeTableCols().col_user, $i18n.locale) || $t('home.member') }}</th>
              <th class="is-vip">{{ siteStore.getLocalizedText(siteStore.homeTableCols().col_vip, $i18n.locale) || 'VIP' }}</th>
            </tr>
          </thead>
          <tbody>
            <!-- 单文件大小 -->
            <tr>
              <td>{{ $t('home.singleFile') }}</td>
              <td>{{ currentGuestSizeMB }} MB</td>
              <td class="is-em">{{ currentUserSizeMB }} MB</td>
              <td class="is-vip">{{ currentVipSizeMB }} MB</td>
            </tr>
            <!-- 上传频率 -->
            <tr>
              <td>{{ $t('home.frequency') }}</td>
              <td>{{ guestRateLimitText }}</td>
              <td class="is-em">{{ userRateLimitText }}</td>
              <td class="is-vip">{{ vipRateLimitText }}</td>
            </tr>
            <!-- 创建相册/文件夹 -->
            <tr>
              <td>
                <template v-if="uploadMode === 'image'">{{ $t('home.createAlbum') }}</template>
                <template v-else-if="uploadMode === 'video'">{{ $t('home.createFolder') }}</template>
                <template v-else>{{ $t('home.createFolder') }}</template>
              </td>
              <td class="is-muted">—</td>
              <td class="is-em">✓</td>
              <td class="is-vip">✓</td>
            </tr>
            <!-- 自定义文件名 -->
            <tr>
              <td>{{ $t('home.customNaming') }}</td>
              <td class="is-muted">—</td>
              <td class="is-em">✓</td>
              <td class="is-vip">✓</td>
            </tr>
            <!-- 批量管理 -->
            <tr>
              <td>{{ $t('home.batchManagement') }}</td>
              <td class="is-muted">—</td>
              <td class="is-em">✓</td>
              <td class="is-vip">✓</td>
            </tr>
            <!-- 图片模式特有功能 -->
            <template v-if="uploadMode === 'image'">
              <!-- 图片水印 -->
              <tr>
                <td>{{ $t('home.imageWatermark') }}</td>
                <td class="is-muted">—</td>
                <td class="is-muted">—</td>
                <td class="is-vip">✓</td>
              </tr>
              <!-- AI 智能分析 -->
              <tr>
                <td>{{ $t('home.aiAnalysis') }}</td>
                <td class="is-muted">—</td>
                <td class="is-muted">—</td>
                <td class="is-vip">✓</td>
              </tr>
              <!-- OCR 文字识别 -->
              <tr>
                <td>{{ $t('home.ocrRecognition') }}</td>
                <td class="is-muted">—</td>
                <td class="is-em">✓</td>
                <td class="is-vip">✓</td>
              </tr>
              <!-- 在线图片编辑 -->
              <tr>
                <td>{{ $t('home.imageEditor') }}</td>
                <td class="is-muted">—</td>
                <td class="is-em">✓</td>
                <td class="is-vip">✓</td>
              </tr>
            </template>
            <!-- 文件模式特有功能 -->
            <template v-else-if="uploadMode === 'file'">
              <tr>
                <td>{{ $t('home.expiration') }}</td>
                <td class="is-muted">1 {{ $t('home.days') }}</td>
                <td class="is-em">✓</td>
                <td class="is-vip">✓</td>
              </tr>
              <tr>
                <td>{{ $t('home.downloadLimit') }}</td>
                <td class="is-muted">—</td>
                <td class="is-em">✓</td>
                <td class="is-vip">✓</td>
              </tr>
            </template>
          </tbody>
        </table>
        
        <router-link v-if="!userStore.isLoggedIn" to="/register" class="cta">
          {{ $t('home.freeRegister') }} <span class="cta__arrow">→</span>
        </router-link>
      </div>
      
      <!-- Right Panel -->
      <div class="home__right">
        <!-- Mode Switcher -->
        <div class="mode-switcher">
          <button 
            class="mode-btn" 
            :class="{ 'is-active': uploadMode === 'image' }"
            @click="uploadMode = 'image'"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/>
            </svg>
            {{ $t('home.modeImage') }}
          </button>
          <button 
            class="mode-btn" 
            :class="{ 'is-active': uploadMode === 'video' }"
            @click="uploadMode = 'video'"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
              <line x1="7" y1="2" x2="7" y2="22"></line>
              <line x1="17" y1="2" x2="17" y2="22"></line>
              <line x1="2" y1="12" x2="22" y2="12"></line>
              <line x1="2" y1="7" x2="7" y2="7"></line>
              <line x1="2" y1="17" x2="7" y2="17"></line>
              <line x1="17" y1="17" x2="22" y2="17"></line>
              <line x1="17" y1="7" x2="22" y2="7"></line>
            </svg>
            {{ $t('home.modeVideo') || 'Video' }}
          </button>
          <button 
            class="mode-btn" 
            :class="{ 'is-active': uploadMode === 'file' }"
            @click="uploadMode = 'file'"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line>
            </svg>
            {{ $t('home.modeFile') }}
          </button>
        </div>

        <!-- Image Settings (Only in Image Mode) -->
        <div v-if="uploadMode === 'image' && !banStatus.is_banned && userStore.isVip" class="file-settings">
             <div class="file-settings__row">
               <div class="setting-toggle">
                 <span class="setting-label" :title="$t('home.autoWatermarkHint')">
                   {{ $t('home.autoWatermark') || '自动添加水印' }}
                 </span>
                 <el-switch v-model="withWatermark" />
               </div>
            </div>
           
           <div class="watermark-inline-settings" v-if="withWatermark">
               <!-- Type (Custom Capsule) -->
               <div class="control-group">
                  <div class="control-label">{{ $t('watermark.type') || '类型' }}</div>
                  <div class="capsule-selector">
                    <button 
                      class="capsule-btn" 
                      :class="{ 'is-active': watermarkConfig.type === 'text' }"
                      @click="watermarkConfig.type = 'text'"
                    >
                      {{ $t('watermark.typeText') || '文字' }}
                    </button>
                    <button 
                      class="capsule-btn" 
                      :class="{ 'is-active': watermarkConfig.type === 'image' }"
                      @click="watermarkConfig.type = 'image'"
                    >
                      {{ $t('watermark.typeImage') || '图片' }}
                    </button>
                  </div>
               </div>

               <!-- Text -->
               <div class="control-group" v-if="watermarkConfig.type === 'text'">
                 <div class="control-label">{{ $t('watermark.text') || '内容' }}</div>
                 <el-input v-model="watermarkConfig.text" size="small" :placeholder="$t('watermark.textPlaceholder') || '请输入文字'" />
               </div>

               <!-- Color & Size for Text -->
                <div class="control-group" style="flex-direction: row; gap: 20px;" v-if="watermarkConfig.type === 'text'">
                    <div>
                        <div class="control-label">{{ $t('watermark.color') || '颜色' }}</div>
                        <el-color-picker v-model="watermarkConfig.color" show-alpha size="small" />
                    </div>
                    <div style="flex: 1">
                        <div class="control-label">{{ $t('watermark.fontSize') || '大小' }}</div>
                        <el-slider v-model="watermarkConfig.size" :min="10" :max="100" size="small" />
                    </div>
                </div>

               <!-- Image -->
               <div class="control-group" v-if="watermarkConfig.type === 'image'">
                  <div class="control-label">{{ $t('watermark.image') || '图片' }}</div>
                  <div class="watermark-upload" @click="triggerWatermarkUpload">
                    <img v-if="watermarkPreviewUrl" :src="watermarkPreviewUrl" class="watermark-preview-img" />
                    <div v-else class="upload-placeholder">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
                      <span>{{ $t('watermark.uploadHint') || '点击上传' }}</span>
                    </div>
                    <input type="file" ref="watermarkInput" style="display: none;" accept="image/png,image/webp" @change="handleWatermarkUpload" />
                  </div>
               </div>

               <!-- Opacity & Position -->
               <div class="control-grid" style="display: grid; grid-template-columns: 1fr 120px; gap: 20px;">
                   <div class="control-group">
                      <div class="control-label">{{ $t('watermark.opacity') || '透明度' }}</div>
                      <el-slider v-model="watermarkConfig.opacity" size="small" />
                   </div>
                   
                   <div class="control-group">
                      <div class="control-label">{{ $t('watermark.position') || '位置' }}</div>
                      <div class="position-grid">
                        <div v-for="pos in ['top-left', 'top-right', 'center', 'bottom-left', 'bottom-right']" 
                             :key="pos"
                             class="position-cell"
                             :class="{ active: watermarkConfig.position === pos }"
                             @click="watermarkConfig.position = pos">
                           <div class="dot"></div>
                        </div>
                      </div>
                   </div>
               </div>
           </div>
        </div>

        <!-- File Settings (Only in File Mode) -->
        <div v-if="uploadMode === 'file' && !banStatus.is_banned" class="file-settings">
          <template v-if="userStore.isLoggedIn">
            <div class="file-settings__row">
              <div class="setting-item">
                <label>{{ $t('home.expiration') }}</label>
                <el-select v-model="fileSettings.expireDays" size="small" style="width: 100%">
                  <el-option 
                    :label="$t('common.unlimited') + (userStore.isVip ? '' : ' (VIP)')" 
                    :value="null" 
                    :disabled="!userStore.isVip"
                  />
                  <el-option :label="`1 ${$t('home.days')}`" :value="1" />
                  <el-option :label="`3 ${$t('home.days')}`" :value="3" />
                  <el-option :label="`7 ${$t('home.days')}`" :value="7" />
                  <el-option :label="`30 ${$t('home.days')}`" :value="30" />
                </el-select>
              </div>
              <div class="setting-item">
                <label>{{ $t('home.downloadLimit') }}</label>
                <el-input 
                  v-model.number="fileSettings.downloadLimit" 
                  size="small" 
                  :placeholder="$t('home.downloadLimitHint')" 
                  type="number"
                  min="1"
                />
              </div>
            </div>
          </template>
          <!-- Guest Tip -->
          <template v-else>
            <div class="guest-tip">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="8"></line></svg>
               {{ $t('home.guestFileTip') || 'Guests: 1 day validity' }}
            </div>
          </template>
          
          <div class="setting-item">
            <label>{{ $t('home.extractionCode') }} <span class="setting-tag">{{ $t('home.optional') }}</span></label>
            <el-input 
              v-model="fileSettings.password" 
              size="small" 
              :placeholder="$t('home.extractionCodeHint')" 
              show-password
            />
          </div>
        </div>

        <div
          class="upload"
          :class="{ 'is-disabled': banStatus.is_banned, 'upload--file-mode': uploadMode === 'file' }"
          @click="!banStatus.is_banned && triggerFileInput()"
          tabindex="0"
          @keydown.enter="!banStatus.is_banned && triggerFileInput()"
          @keydown.space.prevent="!banStatus.is_banned && triggerFileInput()"
        >
          <template v-if="banStatus.is_banned">
            <svg class="upload__icon upload__icon--banned" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <p class="upload__title">{{ $t('home.uploadDisabled') }}</p>
            <p class="upload__hint">{{ $t('home.viewBanDetails') }}</p>
          </template>
          <template v-else>
            <svg class="upload__icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <template v-if="uploadMode === 'image'">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17,8 12,3 7,8"/><line x1="12" y1="3" x2="12" y2="15"/>
              </template>
              <template v-else-if="uploadMode === 'video'">
                <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
                <line x1="7" y1="2" x2="7" y2="22"></line>
                <line x1="17" y1="2" x2="17" y2="22"></line>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <line x1="2" y1="7" x2="7" y2="7"></line>
                <line x1="2" y1="17" x2="7" y2="17"></line>
                <line x1="17" y1="17" x2="22" y2="17"></line>
                <line x1="17" y1="7" x2="22" y2="7"></line>
              </template>
              <template v-else>
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line>
              </template>
            </svg>
            <p class="upload__title">{{ $t('home.dragOrClick') }}</p>
            <p class="upload__hint">{{ $t('home.pasteHint') }}</p>
            <p class="upload__formats">
              <template v-if="uploadMode === 'image'">
                {{ allowedExtensions.join(' / ').toUpperCase() }}
              </template>
              <template v-else-if="uploadMode === 'video'">
                {{ $t('common.videoFiles') }}
              </template>
              <template v-else>
                {{ $t('common.allFiles') || 'ALL FILES' }}
              </template>
              · {{ maxSizeMB }}MB
            </p>
          </template>
        </div>
        
        <input
          ref="fileInput"
          type="file"
          :accept="acceptTypes"
          multiple
          hidden
          @change="handleFileSelect"
        />
      </div>
    </div>
    
    <!-- Upload Results (below the card) -->
    <div v-if="uploadedItems.length > 0" class="results-area">
      <!-- Results -->
      <div class="results">
        <div class="results__head">
          <span>{{ $t('home.uploadSuccess') }} {{ uploadedItems.length }}</span>
          <button @click="clearResults">{{ $t('home.clearResults') }}</button>
        </div>
        
        <div v-for="item in uploadedItems" :key="item.id" class="result-card">
          <!-- Image Result -->
          <template v-if="item.type === 'image'">
            <img :src="item.url" :alt="item.original_filename" class="result-card__thumb" />
            <div class="result-card__info">
              <div class="result-card__name">{{ item.original_filename }}</div>
              <div class="result-card__meta">{{ item.width }}×{{ item.height }} · {{ formatSize(item.file_size) }}</div>
            </div>
            <div class="result-card__links">
              <div class="link-row">
                <span class="link-row__label">URL</span>
                <input :value="item.fullUrl" readonly @focus="$event.target.select()" />
                <button @click="copyToClipboard(item.fullUrl)" :title="$t('common.copy')">{{ $t('common.copy') }}</button>
              </div>
              <div class="link-row">
                <span class="link-row__label">MD</span>
                <input :value="item.markdown" readonly @focus="$event.target.select()" />
                <button @click="copyToClipboard(item.markdown)" :title="$t('common.copy')">{{ $t('common.copy') }}</button>
              </div>
            </div>
          </template>
          
          <!-- File Result -->
          <template v-else>
             <div class="result-card__icon">
               <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                 <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                 <text x="8" y="18" font-size="6" font-weight="bold" fill="currentColor">{{ item.extension?.toUpperCase() || 'FILE' }}</text>
               </svg>
             </div>
             <div class="result-card__info">
               <div class="result-card__name">{{ item.original_filename }}</div>
               <div class="result-card__meta">
                 {{ formatSize(item.file_size) }}
                 <span v-if="item.expire_at" class="meta-tag">{{ $t('home.validity') }}: {{ formatDateTime(item.expire_at) }}</span>
                 <span v-if="item.download_limit" class="meta-tag">{{ $t('home.times') }}: {{ item.download_limit }}</span>
               </div>
             </div>
             <div class="result-card__links">
                <div class="link-row">
                  <span class="link-row__label">LINK</span>
                  <input :value="item.shareLink" readonly @focus="$event.target.select()" />
                  <button @click="copyToClipboard(item.shareLink)" :title="$t('home.copyLink')">{{ $t('home.copyLink') }}</button>
                </div>
                <div v-if="item.access_password" class="link-row">
                  <span class="link-row__label">CODE</span>
                  <input :value="item.access_password" readonly @focus="$event.target.select()" />
                  <button @click="copyToClipboard(item.access_password)" :title="$t('common.copy')">{{ $t('common.copy') }}</button>
                </div>
             </div>
          </template>
        </div>
      </div>
    </div>
    
    <!-- Appeal Dialog -->
    <div v-if="showAppealDialog" class="dialog-overlay" @click.self="showAppealDialog = false">
      <div class="dialog">
        <div class="dialog__header">
          <h3>{{ $t('appeal.submitAppeal') }}</h3>
          <button class="dialog__close" @click="showAppealDialog = false">&times;</button>
        </div>
        <div class="dialog__body">
          <p class="dialog__hint">{{ $t('appeal.appealHint') }}</p>
          <textarea 
            v-model="appealReason" 
            class="dialog__textarea"
            :placeholder="$t('appeal.appealReasonPlaceholder')"
            rows="4"
          ></textarea>
        </div>
        <div class="dialog__footer">
          <button class="btn btn--secondary" @click="showAppealDialog = false">{{ $t('common.cancel') }}</button>
          <button 
            class="btn btn--primary" 
            @click="submitAppeal" 
            :disabled="!appealReason.trim() || submittingAppeal"
          >
            {{ submittingAppeal ? $t('common.loading') : $t('appeal.submitAppeal') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useSiteStore } from '@/stores/site'
import { useThemeStore } from '@/stores/theme'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import api from '@/api'
import { formatDateTime } from '@/utils/timezone'
import UploadOverlay from '@/components/UploadOverlay.vue'
import UploadProgress from '@/components/UploadProgress.vue'

const { t } = useI18n()
const userStore = useUserStore()
const siteStore = useSiteStore()
const themeStore = useThemeStore()

// Logo based on theme - use dark logo if available in dark mode
const currentLogo = computed(() => {
  if (themeStore.isDark && siteStore.siteLogoDark()) {
    return siteStore.siteLogoDark()
  }
  return siteStore.siteLogo()
})
const fileInput = ref(null)
const isDragover = ref(false)
const uploadingFiles = ref([])
const uploadedItems = ref([])
const uploadMode = ref('image')

// File Settings
const fileSettings = reactive({
  expireDays: null,
  downloadLimit: null,
  password: ''
})
const withWatermark = ref(false)

// Ban status
const banStatus = reactive({
  is_banned: false,
  ban_id: null,
  reason: null,
  ban_type: null,
  expires_at: null,
  can_appeal: false,
  existing_appeal: null,
})
const showAppealDialog = ref(false)
const appealReason = ref('')
const submittingAppeal = ref(false)

// Watermark Logic
const watermarkConfig = reactive({
  type: 'text',
  text: '',
  image_path: '',
  opacity: 50,
  position: 'bottom-right',
  size: 20,
  color: '#FFFFFF'
})
const watermarkInput = ref(null)
const watermarkPreviewUrl = ref('')

onMounted(() => {
  const saved = localStorage.getItem('watermarkConfig')
  if (saved) {
    try {
      Object.assign(watermarkConfig, JSON.parse(saved))
      if (watermarkConfig.image_path) {
        watermarkPreviewUrl.value = `/uploads/${watermarkConfig.image_path}`
      }
    } catch (e) {}
  }
})

watch(watermarkConfig, (val) => {
  localStorage.setItem('watermarkConfig', JSON.stringify(val))
}, { deep: true })

const triggerWatermarkUpload = () => watermarkInput.value?.click()

const handleWatermarkUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    watermarkConfig.image_path = response.data.file_path
    watermarkPreviewUrl.value = `/uploads/${response.data.file_path}`
    ElMessage.success(t('common.uploadSuccess'))
  } catch (error) {
    ElMessage.error(t('error.uploadFailed'))
  }
}


// Dynamic settings from database
const allowedExtensions = computed(() => siteStore.allowedExtensions())
const acceptTypes = computed(() => {
  if (uploadMode.value === 'file') return '*/*'
  if (uploadMode.value === 'video') return 'video/*'
  return siteStore.allowedExtensions().map(ext => `image/${ext === 'jpg' ? 'jpeg' : ext}`).join(',')
})

// Dynamic Size Limits based on Mode
const currentGuestSizeMB = computed(() => {
  if (uploadMode.value === 'video') return siteStore.maxSizeGuestVideoMB() || 20
  if (uploadMode.value === 'file') return siteStore.maxSizeGuestFileMB() || 100
  return siteStore.maxSizeGuestMB()
})

const currentUserSizeMB = computed(() => {
  if (uploadMode.value === 'video') return siteStore.maxSizeUserVideoMB() || 100
  if (uploadMode.value === 'file') return siteStore.maxSizeUserFileMB() || 512
  return siteStore.maxSizeUserMB()
})

const currentVipSizeMB = computed(() => {
  if (uploadMode.value === 'video') return siteStore.maxSizeVipVideoMB() || 1024
  if (uploadMode.value === 'file') return siteStore.maxSizeVipFileMB() || 2048
  return siteStore.maxSizeVipMB()
})

const maxSizeMB = computed(() => userStore.isLoggedIn ? currentUserSizeMB.value : currentGuestSizeMB.value)
const maxSizeBytes = computed(() => maxSizeMB.value * 1024 * 1024)

// Rate limits - only show per hour for cleaner display
const rateLimitUnit = computed(() => {
  return (uploadMode.value === 'file' || uploadMode.value === 'video') ? t('home.perHourTimes') : t('home.perHour')
})
const guestRateLimitText = computed(() => {
  if (uploadMode.value === 'video') return `${siteStore.guestVideoLimitPerHour()}${rateLimitUnit.value}`
  if (uploadMode.value === 'file') return `${siteStore.guestFileLimitPerHour()}${rateLimitUnit.value}`
  return `${siteStore.guestRateLimitPerHour()}${rateLimitUnit.value}`
})
const userRateLimitText = computed(() => {
  if (uploadMode.value === 'video') return `${siteStore.userVideoLimitPerHour()}${rateLimitUnit.value}`
  if (uploadMode.value === 'file') return `${siteStore.userFileLimitPerHour()}${rateLimitUnit.value}`
  return `${siteStore.userRateLimitPerHour()}${rateLimitUnit.value}`
})
const vipRateLimitText = computed(() => {
  if (uploadMode.value === 'video') return `${siteStore.vipVideoLimitPerHour()}${rateLimitUnit.value}`
  if (uploadMode.value === 'file') return `${siteStore.vipFileLimitPerHour()}${rateLimitUnit.value}`
  return `${siteStore.vipRateLimitPerHour()}${rateLimitUnit.value}`
})

const triggerFileInput = () => fileInput.value?.click()

// Global Drag Handling
let dragCounter = 0
const handleDragEnter = (e) => {
  e.preventDefault()
  dragCounter++
  if (dragCounter === 1) {
    isDragover.value = true
  }
}

const handleDragLeave = (e) => {
  e.preventDefault()
  dragCounter--
  if (dragCounter === 0) {
    isDragover.value = false
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragover.value = false
  dragCounter = 0
  
  if (banStatus.is_banned) return
  
  const files = Array.from(e.dataTransfer.files)
  // Smart switch mode if dropped non-image in image mode?
  // For now simpler: Use current mode logic, or filter
  if (uploadMode.value === 'image') {
     const images = files.filter(f => f.type.startsWith('image/'))
     if (images.length) uploadFiles(images)
  } else {
     if (files.length) uploadFiles(files)
  }
}

const handleDragOver = (e) => {
  e.preventDefault()
  // Needed to allow drop
}

const handleFileSelect = (e) => {
  uploadFiles(Array.from(e.target.files))
  e.target.value = ''
}

const handlePaste = (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
  const items = e.clipboardData?.items
  if (!items) return
  const files = []
  for (const item of items) {
    // In file mode, basic clipboard file support might be limited by browser
    // But image pasting is common
    if (item.kind === 'file') {
       const file = item.getAsFile()
       if (file) files.push(file)
    }
  }
  
  if (files.length > 0) {
    // If current mode is image but file is not image, maybe warn?
    // Let validation handle it
    uploadFiles(files)
  }
}

const validateFile = (file) => {
  if (uploadMode.value === 'image') {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!allowedExtensions.value.includes(ext) && !file.type.startsWith('image/')) {
      ElMessage.error(t('error.unsupportedFormat', { format: file.name }))
      return false
    }
  } else if (uploadMode.value === 'video') {
    if (!file.type.startsWith('video/')) {
       ElMessage.error(t('error.unsupportedFormat', { format: file.name }))
       return false
    }
  }
  
  if (file.size > maxSizeBytes.value) {
    ElMessage.error(t('error.fileTooLarge', { size: maxSizeMB.value }))
    return false
  }
  return true
}

import { uploadChunked } from '@/utils/chunkUpload'

const uploadFiles = async (files) => {
  for (const file of files) {
    if (!validateFile(file)) continue
    
    // Create progress item
    const item = reactive({ 
      id: Date.now() + Math.random(), 
      name: file.name, 
      progress: 0, 
      status: 'uploading' 
    })
    uploadingFiles.value.unshift(item)
    
    try {
      // Logic for large files (Chunked Upload)
      // Use chunked for anything > 30MB to be safe and robust
      const CHUNK_THRESHOLD = 30 * 1024 * 1024;
      
      if (file.size > CHUNK_THRESHOLD) {
          // Use Chunked Upload
          const resultData = await uploadChunked(file, {
              onProgress: (p) => { item.progress = p },
              settings: fileSettings,
              uploadMode: uploadMode.value // used mainly for stats or type hint if needed
          })
          
          // Chunk upload handles different types
          if (resultData.type === 'image') {
              const imageUrl = resultData.url
              const fullUrl = imageUrl.startsWith('http') ? imageUrl : window.location.origin + imageUrl
              uploadedItems.value.unshift({
                  type: 'image',
                  ...resultData.image,
                  url: imageUrl,
                  fullUrl,
                  markdown: resultData.markdown || `![${resultData.image.original_filename}](${fullUrl})`,
                  html: `<img src="${fullUrl}" alt="${resultData.image.original_filename}">`,
              })
          } else {
              const shareLink = resultData.shareLink || `${window.location.origin}/s/${resultData.unique_code}`
              uploadedItems.value.unshift({
                  type: 'file',
                  ...resultData,
                  shareLink,
              })
          }
          
      } else {
          // Standard Upload
          const formData = new FormData()
          formData.append('file', file)
          
          let res
          
          if (uploadMode.value === 'image') {
            // Image Upload
            if (withWatermark.value) {
              formData.append('with_watermark', 'true')
              formData.append('watermark_config', JSON.stringify(watermarkConfig))
            }
            res = await api.post('/upload', formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
              onUploadProgress: (e) => { item.progress = Math.round((e.loaded / e.total) * 100) },
            })
            
            const imageUrl = res.data.url
            const fullUrl = imageUrl.startsWith('http') ? imageUrl : window.location.origin + imageUrl
            
            uploadedItems.value.unshift({
              type: 'image',
              ...res.data.image,
              url: imageUrl,
              fullUrl,
              markdown: `![${res.data.image.original_filename}](${fullUrl})`,
              html: `<img src="${fullUrl}" alt="${res.data.image.original_filename}">`,
            })
            
          } else {
            // File Upload
            
            // Settings Handling
            if (uploadMode.value === 'file') {
              if (userStore.isLoggedIn) {
                // Logged in user: use selected settings
                if (fileSettings.password) formData.append('password', fileSettings.password)
                if (fileSettings.downloadLimit) formData.append('download_limit', fileSettings.downloadLimit)
                
                if (fileSettings.expireDays) {
                  const date = new Date()
                  date.setDate(date.getDate() + fileSettings.expireDays)
                  formData.append('expire_at', date.toISOString())
                }
              } else {
                // Guest: Force 1 day expiration, no download limit custom
                if (fileSettings.password) formData.append('password', fileSettings.password)
                
                const date = new Date()
                date.setDate(date.getDate() + 1) // Force 1 day
                formData.append('expire_at', date.toISOString())
              }
            }
            
            res = await api.post('/files/upload', formData, {
               headers: { 'Content-Type': 'multipart/form-data' },
               onUploadProgress: (e) => { item.progress = Math.round((e.loaded / e.total) * 100) },
            })
            
            const fileData = res.data
            const shareLink = `${window.location.origin}/s/${fileData.unique_code}`
            
            uploadedItems.value.unshift({
              type: 'file',
              ...fileData,
              shareLink,
            })
          }
      }
      
      item.status = 'success'
    } catch (e) {
      item.status = 'exception'
      console.error(e)
      ElMessage.error(e.response?.data?.detail || t('error.uploadFailed'))
    }
  }
}


const copyToClipboard = async (text) => {
  try {
    // 优先使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      ElMessage.success(t('common.copied'))
      return
    }
    // Fallback: 使用传统方法（支持非 HTTPS 环境）
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-9999px'
    textArea.style.top = '-9999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    const successful = document.execCommand('copy')
    document.body.removeChild(textArea)
    if (successful) {
      ElMessage.success(t('common.copied'))
    } else {
      ElMessage.error(t('error.copyFailed'))
    }
  } catch {
    ElMessage.error(t('error.copyFailed'))
  }
}

const clearResults = () => { uploadedItems.value = [] }

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

// Ban status functions
const checkBanStatus = async () => {
  if (!userStore.isLoggedIn) {
    // Reset ban status for guests (they'll get error on upload attempt)
    Object.assign(banStatus, {
      is_banned: false,
      ban_id: null,
      reason: null,
      ban_type: null,
      expires_at: null,
      can_appeal: false,
      existing_appeal: null,
    })
    return
  }
  
  try {
    const res = await api.get('/appeal/status')
    Object.assign(banStatus, res.data)
  } catch (e) {
    console.error('Failed to check ban status:', e)
  }
}

const formatBanExpiry = (dateStr) => {
  return formatDateTime(dateStr, siteStore.timezone())
}

const getAppealStatusText = (status) => {
  const statusMap = {
    pending: t('appeal.statusPending'),
    approved: t('appeal.statusApproved'),
    rejected: t('appeal.statusRejected')
  }
  return statusMap[status] || status
}

const submitAppeal = async () => {
  if (!appealReason.value.trim()) return
  
  submittingAppeal.value = true
  try {
    await api.post('/appeal', { reason: appealReason.value.trim() })
    ElMessage.success(t('appeal.submitSuccess'))
    showAppealDialog.value = false
    appealReason.value = ''
    // Refresh ban status to show appeal
    await checkBanStatus()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('error.saveFailed'))
  } finally {
    submittingAppeal.value = false
  }
}

// Watch for login status changes
watch(() => userStore.isLoggedIn, () => {
  checkBanStatus()
})

// Watch for VIP status and upload mode to enforce expiration policies
watch([() => userStore.isVip, uploadMode], ([isVip, mode]) => {
  if (mode === 'file' && !isVip && fileSettings.expireDays === null) {
    if (userStore.isLoggedIn) {
      fileSettings.expireDays = 7 // Default for non-VIP members
    }
  }
}, { immediate: true })

onMounted(() => {
  document.addEventListener('paste', handlePaste)
  
  // Register global drag events
  window.addEventListener('dragenter', handleDragEnter)
  window.addEventListener('dragleave', handleDragLeave)
  window.addEventListener('dragover', handleDragOver)
  window.addEventListener('drop', handleDrop)
  
  checkBanStatus()
})

onUnmounted(() => {
  document.removeEventListener('paste', handlePaste)
  
  // Remove global drag events
  window.removeEventListener('dragenter', handleDragEnter)
  window.removeEventListener('dragleave', handleDragLeave)
  window.removeEventListener('dragover', handleDragOver)
  window.removeEventListener('drop', handleDrop)
})
</script>

<style lang="scss" scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1; // Fill available space defined by parent
  min-height: 0; // Prevent flex overflow issues
  padding: 32px 48px;
}

// Ban Notice
.ban-notice {
  display: flex;
  gap: 16px;
  max-width: 1000px;
  width: 100%;
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-lg);
  margin-bottom: 24px;
  
  &__icon {
    flex-shrink: 0;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(239, 68, 68, 0.15);
    border-radius: 50%;
    color: #ef4444;
  }
  
  &__content {
    flex: 1;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #ef4444;
      margin: 0 0 8px;
    }
  }
  
  &__reason {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0 0 4px;
  }
  
  &__expires {
    font-size: 13px;
    color: var(--text-tertiary);
    margin: 0 0 12px;
    
    &--permanent {
      color: #ef4444;
      font-weight: 500;
    }
  }
  
  &__appeal {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(239, 68, 68, 0.15);
  }
  
  &__login-hint {
    font-size: 13px;
    color: var(--text-tertiary);
    margin: 12px 0 0;
    
    a {
      color: var(--accent-primary);
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

.appeal-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  
  &__label {
    font-size: 13px;
    color: var(--text-tertiary);
  }
  
  &__value {
    font-size: 13px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 4px;
    
    &--pending {
      background: rgba(234, 179, 8, 0.15);
      color: #ca8a04;
    }
    
    &--approved {
      background: rgba(34, 197, 94, 0.15);
      color: #16a34a;
    }
    
    &--rejected {
      background: rgba(239, 68, 68, 0.15);
      color: #ef4444;
    }
  }
}

.appeal-response {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 8px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  
  &--appeal {
    background: #ef4444;
    color: white;
    border-color: #ef4444;
    
    &:hover {
      background: #dc2626;
      border-color: #dc2626;
    }
  }
  
  &--primary {
    background: var(--accent-primary);
    color: var(--text-inverse);
    border-color: var(--accent-primary);
    
    &:hover {
      opacity: 0.9;
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  &--secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-color: var(--border-medium);
    
    &:hover {
      background: var(--bg-tertiary);
      border-color: var(--border-dark);
    }
  }
}

// Dialog
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.dialog {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-light);
  width: 100%;
  max-width: 480px;
  
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-light);
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
  }
  
  &__close {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: 1px solid transparent;
    font-size: 20px;
    color: var(--text-tertiary);
    cursor: pointer;
    border-radius: 4px;
    
    &:hover {
      background: var(--bg-secondary);
      border-color: var(--border-light);
      color: var(--text-primary);
    }
  }
  
  &__body {
    padding: 20px;
  }
  
  &__hint {
    font-size: 13px;
    color: var(--text-tertiary);
    margin: 0 0 12px;
  }
  
  &__textarea {
    width: 100%;
    padding: 12px;
    font-size: 14px;
    color: var(--text-primary);
    background: var(--bg-secondary);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-md);
    resize: vertical;
    min-height: 100px;
    
    &::placeholder {
      color: var(--text-tertiary);
    }
    
    &:focus {
      outline: none;
      border-color: var(--border-dark);
    }
  }
  
  &__footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 20px;
    border-top: 1px solid var(--border-light);
  }
}

.home__card {
  display: flex;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-light);
  overflow: hidden;
  max-width: 1400px; /* Increased to 1400px */
  width: 100%;
  min-height: 520px; /* Increased height */
}

.home__left {
  flex: 0 0 520px; /* Increased to 520px */
  padding: 48px 42px; /* Adjusted padding */
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
}

.home__right {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 48px;
  position: relative;
}

// Mode Switcher
.mode-switcher {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  
  svg { opacity: 0.7; }
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
  
  &.is-active {
    background: var(--accent-primary);
    color: white;
    box-shadow: var(--shadow-colored);
    svg { opacity: 1; }
  }
}

// Checkbox
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  user-select: none;
  
  input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--accent-primary);
    cursor: pointer;
  }
}

.setting-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.setting-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

// File Settings
.file-settings {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  margin-bottom: 20px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &__row {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.watermark-inline-settings {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-light);
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  animation: fadeIn 0.3s ease;
  
  .control-group {
    margin-bottom: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .control-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
  }
}

.capsule-selector {
  display: flex;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
  padding: 3px;
  border: 1px solid var(--border-light);
  width: fit-content;
}

.capsule-btn {
  padding: 4px 16px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-tertiary);
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    color: var(--text-secondary);
  }
  
  &.is-active {
    background: var(--bg-card);
    color: var(--accent-primary);
    box-shadow: var(--shadow-sm);
  }
}

.watermark-upload {
  width: 100%;
  height: 120px;
  border: 2px dashed var(--border-medium);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(var(--accent-rgb), 0.08) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s;
  }
  
  &:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(var(--accent-rgb), 0.15),
                0 0 0 1px rgba(var(--accent-rgb), 0.1);
    
    &::before { opacity: 1; }
    
    .upload-placeholder {
        color: var(--accent-primary);
        svg { 
          transform: translateY(-3px) scale(1.1);
          color: var(--accent-primary);
        }
    }
  }
  
  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    color: var(--text-tertiary);
    font-size: 13px;
    font-weight: 500;
    transition: all 0.3s;
    
    svg { 
        width: 28px;
        height: 28px;
        opacity: 0.7; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
  }
  
  .watermark-preview-img {
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15));
    z-index: 1;
    transition: transform 0.3s;
  }
  
  &:hover .watermark-preview-img {
    transform: scale(1.05);
  }
}

.position-grid {
  display: grid;
  grid-template-areas: 
    "tl . tr"
    ".  c  ."
    "bl . br";
  gap: 6px;
  width: 100px;
  height: 60px;
  background: var(--bg-secondary);
  padding: 6px;
  border-radius: 8px;
  
  .position-cell {
    border-radius: 4px;
    cursor: pointer;
    background: rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    
    &:hover { background: rgba(255,255,255,0.1); }
    &.active { 
        background: var(--accent-primary); 
        .dot { background: white; }
    }
    
    .dot {
        width: 4px; 
        height: 4px; 
        border-radius: 50%; 
        background: var(--text-tertiary);
    }
    
    &:nth-child(1) { grid-area: tl; }
    &:nth-child(2) { grid-area: tr; }
    &:nth-child(3) { grid-area: c; }
    &:nth-child(4) { grid-area: bl; }
    &:nth-child(5) { grid-area: br; }
  }
}

.setting-item {
  label {
    display: block;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-tertiary);
    margin-bottom: 6px;
    
    .setting-tag {
      background: var(--bg-tertiary);
      padding: 1px 4px;
      border-radius: 4px;
      font-size: 10px;
      margin-left: 4px;
    }
  }
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.guest-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-tertiary);
  background: var(--bg-tertiary);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  margin-bottom: 12px;
  
  svg {
    opacity: 0.7;
  }
}

// Upload Area (Unified)
.upload {
  flex: 1;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  border: 2px dashed var(--border-medium);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 280px;
  text-align: center;
  padding: 40px;
  position: relative;
  overflow: hidden;
  
  // Subtle gradient overlay
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 0%, rgba(var(--accent-rgb), 0.05) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
  }
  
  &:hover:not(.is-disabled) {
    border-color: var(--accent-primary);
    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-card) 100%);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 
                0 0 0 1px rgba(var(--accent-rgb), 0.1);
    transform: translateY(-2px);
    
    &::before {
      opacity: 1;
    }
    
    .upload__icon {
      color: var(--accent-primary);
      transform: scale(1.15) translateY(-4px);
    }
    
    .upload__title {
      color: var(--accent-primary);
    }
  }
  
  &--file-mode {
    border-color: var(--accent-secondary); 
    
    &:hover:not(.is-disabled) {
      border-color: var(--accent-secondary);
      .upload__icon {
        color: var(--accent-secondary);
      }
    }
  }
  
  &.is-disabled {
    cursor: not-allowed;
    opacity: 0.6;
    background: var(--bg-secondary);
    border-color: var(--border-light);
    
    &:hover {
      border-color: var(--border-light);
      background: var(--bg-secondary);
      transform: none;
      box-shadow: none;
      .upload__icon { transform: none; }
    }
  }
  
  &__icon {
    color: var(--text-tertiary);
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
    
    &--banned {
      color: #ef4444;
    }
  }
  
  &__title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px;
    transition: color 0.3s;
  }
  
  &__hint {
    font-size: 14px;
    color: var(--text-tertiary);
    margin: 0 0 24px;
  }
  
  &__formats {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-tertiary);
    padding: 8px 16px;
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border-radius: 24px;
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-sm);
  }
}

// Results Area
.results-area {
  width: 100%;
  max-width: 1400px;
  margin-top: 32px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.results {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  overflow: hidden;
  
  &__head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-light);
    background: var(--bg-secondary);
    font-weight: 500;
    font-size: 14px;
    
    button {
      background: none;
      border: none;
      color: var(--accent-primary);
      cursor: pointer;
      font-size: 13px;
      
      &:hover { text-decoration: underline; }
    }
  }
}

.result-card {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-light);
  gap: 20px;
  
  &:last-child {
    border-bottom: none;
  }
  
  &__thumb {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: var(--radius-md);
    background: var(--bg-secondary);
  }
  
  &__icon {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
  }
  
  &__info {
    flex: 1;
    min-width: 0;
  }
  
  &__name {
    font-size: 15px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  &__meta {
    font-size: 13px;
    color: var(--text-tertiary);
    display: flex;
    gap: 8px;
    align-items: center;
    
    .meta-tag {
      background: var(--bg-tertiary);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 11px;
    }
  }
  
  &__links {
    flex: 0 0 320px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.link-row {
  display: flex;
  align-items: center;
  gap: 8px;
  
  &__label {
    width: 36px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
  }
  
  input {
    flex: 1;
    padding: 6px 10px;
    background: var(--bg-secondary);
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    font-size: 12px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
    
    &:focus {
      outline: none;
      background: var(--bg-tertiary);
      color: var(--text-primary);
    }
  }
  
  button {
    padding: 6px 10px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    font-size: 12px;
    cursor: pointer;
    white-space: nowrap;
    
    &:hover {
      background: var(--bg-tertiary);
      color: var(--text-primary);
    }
  }
}


// Brand
.brand {
  margin-bottom: 28px;
  
  &__logo {
    // 固定高度，宽度自适应，避免切换时跳动
    height: 48px;
    width: auto;
    max-width: 180px;
    object-fit: contain;
    // 平滑过渡
    transition: opacity 0.2s ease;
  }
  
  &__name {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
  }
  
  &__tagline {
    font-size: 14px;
    color: var(--text-tertiary);
    margin-top: 6px;
  }
}

// Features List
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  justify-items: center; /* Center items and let them fit content width */
  gap: 12px;
  margin-bottom: 32px;
  width: 100%;
}

.feature {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg-surface);
  padding: 8px 16px;
  border-radius: 99px;
  border: 1px solid var(--border-light);
  white-space: nowrap;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--accent-primary);
    background: var(--bg-secondary);
  }
  
  &__icon {
    color: var(--success);
    flex-shrink: 0;
  }
}

.divider {
  height: 1px;
  background: var(--border-light);
  margin-bottom: 32px;
}

// Comparison Table
.compare {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 32px;
  font-size: 14px;
  
  th {
    text-align: left;
    padding-bottom: 16px;
    font-weight: 500;
    color: var(--text-tertiary);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    
    &.is-vip { color: #f59e0b; }
  }
  
  td {
    padding: 8px 0;
    color: var(--text-secondary);
    border-bottom: 1px solid transparent;
    
    &.is-muted { color: var(--text-tertiary); opacity: 0.5; }
    &.is-em { color: var(--text-primary); font-weight: 500; }
    &.is-vip { color: #f59e0b; font-weight: 600; }
  }
}

// CTA Button
.cta {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-primary-hover));
  color: var(--text-inverse);
  text-decoration: none;
  border-radius: var(--radius-lg);
  font-weight: 600;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px var(--accent-primary-bg);
    
    .cta__arrow { transform: translateX(4px); }
  }
  
  &__arrow { transition: transform 0.2s; }
}

// Upload Area
.upload {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--border-medium);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(.is-disabled) {
    border-color: var(--accent-primary);
    background: var(--bg-secondary);
    
    .upload__icon { color: var(--accent-primary); transform: translateY(-4px); }
  }
  
  &.is-disabled {
    cursor: default;
    opacity: 0.8;
  }
  
  &__icon {
    color: var(--text-tertiary);
    margin-bottom: 20px;
    transition: all 0.3s ease;
    
    &--banned {
      color: #ef4444;
    }
  }
  
  &__title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px;
  }
  
  &__hint {
    font-size: 14px;
    color: var(--text-tertiary);
    margin: 0 0 24px;
  }
  
  &__formats {
    font-size: 12px;
    color: var(--text-tertiary);
    padding: 6px 12px;
    background: var(--bg-card);
    border-radius: 99px;
    border: 1px solid var(--border-light);
  }
}

// Results Area
.results-area {
  width: 100%;
  max-width: 1000px;
  margin-top: 32px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.results {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  overflow: hidden;
  
  &__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-light);
    background: var(--bg-secondary);
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    
    button {
      font-size: 13px;
      color: var(--text-tertiary);
      background: none;
      border: none;
      cursor: pointer;
      
      &:hover { color: var(--danger); }
    }
  }
}

.result-card {
  display: flex;
  padding: 20px;
  border-bottom: 1px solid var(--border-light);
  gap: 20px;
  
  &:last-child { border-bottom: none; }
  
  &__thumb {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: var(--radius-md);
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
  }
  
  &__info {
    flex: 0 0 200px;
  }
  
  &__name {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
    word-break: break-all;
  }
  
  &__meta {
    font-size: 12px;
    color: var(--text-tertiary);
  }
  
  &__links {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
}

.link-row {
  display: flex;
  align-items: center;
  gap: 12px;
  
  &__label {
    width: 40px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
  }
  
  input {
    flex: 1;
    padding: 8px 12px;
    font-size: 13px;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    font-family: monospace;
    transition: all 0.2s;
    
    &:focus {
      outline: none;
      border-color: var(--accent-primary);
      background: var(--bg-card);
      color: var(--text-primary);
    }
  }
  
  button {
    padding: 8px 12px;
    font-size: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    
    &:hover {
      background: var(--bg-surface);
      color: var(--text-primary);
      border-color: var(--border-medium);
    }
  }
}

// Mobile Responsive
@media (max-width: 768px) {
  .home {
    padding: 20px;
  }
  
  .home__card {
    flex-direction: column;
  }
  
  .home__left {
    flex: none;
    padding: 32px 24px;
  }
  
  .home__right {
    padding: 32px 24px;
    min-height: 300px;
  }
  
  .result-card {
    flex-direction: column;
    
    &__thumb {
      width: 100%;
      height: 200px;
    }
    
    &__info {
      flex: none;
    }
  }
  
  .upload-progress {
    width: calc(100% - 32px);
    bottom: 16px;
    right: 16px;
  }
  
  .features {
    grid-template-columns: 1fr;
    gap: 8px;
    
    .feature {
      justify-content: flex-start;
      background: transparent;
      border: none;
      padding: 4px 0;
      font-size: 14px;
      
      &__icon {
        width: 16px;
        height: 16px;
      }
    }
  }

  .mode-switcher {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    background: var(--bg-secondary);
    padding: 6px;
    border-radius: var(--radius-lg);
    
    .mode-btn {
      flex-direction: column;
      padding: 12px 8px;
      font-size: 12px;
      gap: 6px;
      background: transparent;
      border: none;
      border-radius: var(--radius-md);
      
      svg { width: 20px; height: 20px; }
      
      &.is-active {
        background: var(--bg-card);
        color: var(--accent-primary);
        box-shadow: var(--shadow-sm);
        
        svg { color: var(--accent-primary); }
      }
    }
  }
}
</style>
