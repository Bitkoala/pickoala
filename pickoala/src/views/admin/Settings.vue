<template>
  <div class="admin-page">
    <div class="admin-header">
      <h2 class="admin-page__title">{{ $t('admin.settings') }}</h2>
      <button class="admin-menu-toggle" @click="isMenuOpen = !isMenuOpen">
        <svg v-if="!isMenuOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    
    <div class="settings-layout">
      <!-- Sidebar Navigation -->
      <div class="settings-nav-overlay" v-if="isMenuOpen" @click="isMenuOpen = false"></div>
      <nav class="settings-nav" :class="{ 'is-open': isMenuOpen }">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          class="settings-nav__item"
          :class="{ 'is-active': activeTab === tab.key }"
          @click="selectTab(tab.key)"
        >
          <span class="settings-nav__icon" v-html="tab.icon"></span>
          <span class="settings-nav__text">{{ tab.label }}</span>
        </button>
      </nav>
      
      <!-- Settings Content -->
      <div class="settings-content">
        <!-- General Settings -->
        <div v-show="activeTab === 'general'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.general') }}</h3>
            <p class="section-desc">{{ $t('admin.generalSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.general">
            <h4 class="config-title">{{ $t('admin.basicInfo') }}</h4>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('settings.siteName') }}</span>
                <span class="label-hint">{{ $t('admin.siteNameHint') }}</span>
              </label>
              <input v-model="settings.general.site_name" type="text" class="form-input" placeholder="PicKoala" />
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('settings.siteTitle') }}</span>
                <span class="label-hint">{{ $t('admin.siteTitleHint') }}</span>
              </label>
              <input v-model="settings.general.site_title" type="text" class="form-input" :placeholder="$t('admin.siteTitlePlaceholder')" />
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('settings.siteDescription') }}</span>
                <span class="label-hint">{{ $t('admin.siteDescriptionHint') }}</span>
              </label>
              <textarea v-model="settings.general.site_description" class="form-input form-textarea" rows="2" :placeholder="$t('admin.siteDescriptionPlaceholder')"></textarea>
            </div>
            
            <div class="form-divider"></div>
            <h4 class="config-title">{{ $t('admin.frontendDisplay') }}</h4>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('settings.siteSlogan') }}</span>
                <span class="label-hint">{{ $t('admin.siteSloganHint') }}</span>
              </label>
              <input v-model="settings.general.site_slogan" type="text" class="form-input" :placeholder="$t('admin.siteSloganPlaceholder')" />
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('settings.siteFooter') }}</span>
                <span class="label-hint">{{ $t('admin.siteFooterHint') }}</span>
              </label>
              <input v-model="settings.general.site_footer" type="text" class="form-input" :placeholder="$t('admin.siteFooterPlaceholder')" />
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.siteUrl') }}</span>
                <span class="label-hint">{{ $t('admin.siteUrlHint') }}</span>
              </label>
              <input v-model="settings.general.site_url" type="text" class="form-input" placeholder="https://example.com" />
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('settings.timezone') }}</span>
                <span class="label-hint">{{ $t('admin.timezoneHint') }}</span>
              </label>
              <select v-model="settings.general.timezone" class="form-input form-select">
                <option value="Asia/Shanghai">{{ $t('admin.timezoneChina') }}</option>
                <option value="Asia/Tokyo">{{ $t('admin.timezoneJapan') }}</option>
                <option value="Asia/Singapore">{{ $t('admin.timezoneSingapore') }}</option>
                <option value="Asia/Hong_Kong">{{ $t('admin.timezoneHongKong') }}</option>
                <option value="UTC">{{ $t('admin.timezoneUTC') }}</option>
                <option value="America/New_York">{{ $t('admin.timezoneUSEast') }}</option>
                <option value="America/Los_Angeles">{{ $t('admin.timezoneUSWest') }}</option>
                <option value="Europe/London">{{ $t('admin.timezoneUK') }}</option>
                <option value="Europe/Paris">{{ $t('admin.timezoneEurope') }}</option>
              </select>
            </div>
            
            <div class="form-divider"></div>
            <h4 class="config-title">{{ $t('admin.logoAndIcon') }}</h4>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.siteLogo') }}</span>
                <span class="label-hint">{{ $t('admin.siteLogoHint') }}</span>
              </label>
              <div class="logo-input-group">
                <input v-model="settings.general.site_logo" type="text" class="form-input" :placeholder="$t('admin.siteLogoPlaceholder')" />
                <div v-if="settings.general.site_logo" class="logo-preview">
                  <img :src="settings.general.site_logo" :alt="$t('admin.logoPreview')" @error="handleLogoError" />
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.siteLogoDark') }}</span>
                <span class="label-hint">{{ $t('admin.siteLogoDarkHint') }}</span>
              </label>
              <div class="logo-input-group">
                <input v-model="settings.general.site_logo_dark" type="text" class="form-input" :placeholder="$t('admin.siteLogoDarkPlaceholder')" />
                <div v-if="settings.general.site_logo_dark" class="logo-preview logo-preview--dark">
                  <img :src="settings.general.site_logo_dark" :alt="$t('admin.logoDarkPreview')" @error="handleLogoDarkError" />
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.favicon') }}</span>
                <span class="label-hint">{{ $t('admin.faviconHint') }}</span>
              </label>
              <div class="logo-input-group">
                <input v-model="settings.general.site_favicon" type="text" class="form-input" :placeholder="$t('admin.faviconPlaceholder')" />
                <div v-if="settings.general.site_favicon" class="favicon-preview">
                  <img :src="settings.general.site_favicon" :alt="$t('admin.faviconPreview')" @error="handleFaviconError" />
                </div>
              </div>
            </div>
            
            <div class="form-divider"></div>
            <h4 class="config-title">{{ $t('admin.featureToggles') }}</h4>
            
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableRegistration') }}</span>
                <span class="label-hint">{{ $t('admin.enableRegistrationHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.general.enable_registration" />
                <span class="switch__slider"></span>
              </label>
            </div>

            
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableGuestUpload') }}</span>
                <span class="label-hint">{{ $t('admin.enableGuestUploadHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.general.enable_guest_upload" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
          </div>
        </div>
        

        
        <!-- Appearance Settings -->
        <div v-show="activeTab === 'appearance'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.appearance') }}</h3>
            <p class="section-desc">{{ $t('admin.appearanceSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.appearance">
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.themeMode') }}</span>
                <span class="label-hint">{{ $t('admin.themeModeHint') }}</span>
              </label>
              <div class="radio-group">
                <label class="radio-item" :class="{ 'is-active': settings.appearance.theme_mode === 'light' }">
                  <input type="radio" v-model="settings.appearance.theme_mode" value="light" />
                  <span class="radio-item__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
                  </span>
                  <span class="radio-item__text">☀️ {{ $t('admin.themeLight') }}</span>
                </label>
                <label class="radio-item" :class="{ 'is-active': settings.appearance.theme_mode === 'dark' }">
                  <input type="radio" v-model="settings.appearance.theme_mode" value="dark" />
                  <span class="radio-item__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                  </span>
                  <span class="radio-item__text">🌙 {{ $t('admin.themeDark') }}</span>
                </label>
                <label class="radio-item" :class="{ 'is-active': settings.appearance.theme_mode === 'aurora' }">
                  <input type="radio" v-model="settings.appearance.theme_mode" value="aurora" />
                  <span class="radio-item__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
                  </span>
                  <span class="radio-item__text">🌌 {{ $t('admin.themeAurora') }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Customer Service Settings -->
        <div v-show="activeTab === 'cs'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.cs') }}</h3>
            <p class="section-desc">{{ $t('admin.csSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.cs">
            <!-- Mode Selection -->
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.csMode') }}</span>
                <span class="label-hint">{{ $t('admin.csModeHint') }}</span>
              </label>
              <div class="radio-group">
                <label class="radio-item" :class="{ 'is-active': settings.cs.mode === 'off' }">
                  <input type="radio" v-model="settings.cs.mode" value="off" />
                  <span class="radio-item__text">{{ $t('common.disabled') }}</span>
                </label>
                <label class="radio-item" :class="{ 'is-active': settings.cs.mode === 'crisp' }">
                  <input type="radio" v-model="settings.cs.mode" value="crisp" />
                  <span class="radio-item__text">Crisp</span>
                </label>
                <label class="radio-item" :class="{ 'is-active': settings.cs.mode === 'custom' }">
                  <input type="radio" v-model="settings.cs.mode" value="custom" />
                  <span class="radio-item__text">{{ $t('admin.csModeCustom') }}</span>
                </label>
              </div>
            </div>
            
            <!-- Crisp Config -->
            <template v-if="settings.cs.mode === 'crisp'">
              <div class="form-divider"></div>
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.crispWebsiteId') }}</span>
                </label>
                <input v-model="settings.cs.crisp_id" type="text" class="form-input" placeholder="e.g. e50e2b74-..." />
              </div>
            </template>
            
            <!-- Custom Config -->
            <template v-if="settings.cs.mode === 'custom'">
              <div class="form-divider"></div>
              <h4 class="config-title">{{ $t('admin.csCustomConfig') }}</h4>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.csDialogTitle') }}</span>
                </label>
                <input v-model="settings.cs.custom_title" type="text" class="form-input" />
              </div>

              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.csQrCode') }}</span>
                  <span class="label-hint">{{ $t('admin.csQrCodeHint') }}</span>
                </label>
                <div class="logo-input-group">
                  <input v-model="settings.cs.custom_qr" type="text" class="form-input" placeholder="https://..." />
                  <div v-if="settings.cs.custom_qr" class="logo-preview">
                    <img :src="settings.cs.custom_qr" alt="QR Preview" />
                  </div>
                </div>
              </div>

              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.csDescText') }}</span>
                </label>
                <textarea v-model="settings.cs.custom_desc" class="form-input form-textarea" rows="2"></textarea>
              </div>

              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.csLink') }}</span>
                  <span class="label-hint">{{ $t('admin.csLinkHint') }}</span>
                </label>
                <input v-model="settings.cs.custom_link" type="text" class="form-input" />
              </div>

              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.csLinkText') }}</span>
                </label>
                <input v-model="settings.cs.custom_link_text" type="text" class="form-input" />
              </div>
            </template>
          </div>
        </div>

        <!-- Upload Settings -->
        <div v-show="activeTab === 'upload'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.upload') }}</h3>
            <p class="section-desc">{{ $t('admin.uploadSettingsDesc') }}</p>
          </div>
          
          <!-- Image Module -->
          <div class="settings-card" v-if="settings.upload" style="margin-bottom: 24px">
            <div class="card-header" style="margin-bottom: 24px; display: flex; align-items: center; gap: 8px; padding-bottom: 16px; border-bottom: 1px solid var(--border-light);">
               <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--accent-primary);">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <polyline points="21 15 16 10 5 21"></polyline>
               </svg>
               <h4 class="config-title" style="margin: 0; font-size: 16px;">{{ $t('admin.imageSettings') || 'Image Settings' }}</h4>
            </div>

            <!-- Image Size Limits -->
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.guestSizeLimit') }}</span>
                <span class="label-hint">{{ $t('admin.guestSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="guestSizeMB" type="number" class="form-input" min="1" max="100" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.userSizeLimit') }}</span>
                <span class="label-hint">{{ $t('admin.userSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="userSizeMB" type="number" class="form-input" min="1" max="100" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">VIP {{ $t('admin.userSizeLimit') }}</span>
                <span class="label-hint">VIP {{ $t('admin.userSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="vipSizeMB" type="number" class="form-input" min="1" max="500" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>
            
            <div class="form-divider"></div>
            
            <!-- Image Configs -->
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.allowedFormats') }}</span>
                <span class="label-hint">{{ $t('admin.allowedFormatsHint') }}</span>
              </label>
              <input v-model="settings.upload.allowed_extensions" type="text" class="form-input" placeholder="png,jpg,jpeg,gif,webp" />
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.compressionQuality') }}</span>
                <span class="label-hint">{{ $t('admin.compressionQualityHint') }}</span>
              </label>
              <div class="slider-input">
                <input 
                  type="range" 
                  v-model.number="settings.upload.compression_quality" 
                  min="10" 
                  max="100" 
                  class="slider"
                />
                <span class="slider-value">{{ settings.upload.compression_quality }}%</span>
              </div>
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.maxDimension') }}</span>
                <span class="label-hint">{{ $t('admin.maxDimensionHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="settings.upload.max_dimension" type="number" class="form-input" min="0" placeholder="4096" />
                <span class="input-group__suffix">{{ $t('admin.pixels') }}</span>
              </div>
            </div>

            <div class="form-divider"></div>
            
            <!-- Image Rate Limits -->
             <h4 class="config-title">{{ $t('admin.imageRateLimits') }}</h4>
            
            <!-- Guest -->
            <h4 class="rate-limit-title">{{ $t('admin.guest') }}</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>

            <div class="form-divider"></div>

            <!-- User -->
            <h4 class="rate-limit-title">{{ $t('admin.member') }}</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>

            <div class="form-divider"></div>

            <!-- VIP -->
            <h4 class="rate-limit-title">VIP</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Video Module -->
          <div class="settings-card" v-if="settings.upload" style="margin-bottom: 24px">
            <div class="card-header" style="margin-bottom: 24px; display: flex; align-items: center; gap: 8px; padding-bottom: 16px; border-bottom: 1px solid var(--border-light);">
               <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--accent-primary);">
                  <polygon points="23 7 16 12 23 17 23 7"></polygon>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
               </svg>
               <h4 class="config-title" style="margin: 0; font-size: 16px;">{{ $t('admin.videoSettings') || 'Video Settings' }}</h4>
            </div>

            <!-- Video Size Limits -->
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.guestSizeLimit') }}</span>
                <span class="label-hint">{{ $t('admin.guestSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="guestVideoSizeMB" type="number" class="form-input" min="1" max="1000" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.userSizeLimit') }}</span>
                <span class="label-hint">{{ $t('admin.userSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="userVideoSizeMB" type="number" class="form-input" min="1" max="5000" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">VIP {{ $t('admin.userSizeLimit') }}</span>
                <span class="label-hint">VIP {{ $t('admin.userSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="vipVideoSizeMB" type="number" class="form-input" min="1" max="10240" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>
            
            <div class="form-divider"></div>
            
            <!-- Video Allowed Extensions -->
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.allowedFormats') }}</span>
                <span class="label-hint">{{ $t('admin.allowedFormatsHint') || 'Comma separated extensions' }}</span>
              </label>
              <input v-model="settings.upload.video_allowed_extensions" type="text" class="form-input" placeholder="mp4,webm,ogg,mov,mkv" />
            </div>

            <div class="form-divider"></div>
            
            <!-- Video Rate Limits -->
            <h4 class="config-title">{{ $t('admin.videoRateLimits') || 'Video Rate Limits' }}</h4>
            
            <!-- Guest -->
            <h4 class="rate-limit-title">{{ $t('admin.guest') }}</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_video_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_video_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_video_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>

            <div class="form-divider"></div>

            <!-- User -->
            <h4 class="rate-limit-title">{{ $t('admin.member') }}</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_video_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_video_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_video_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>

            <div class="form-divider"></div>

            <!-- VIP -->
            <h4 class="rate-limit-title">VIP</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_video_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_video_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_video_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- File Module -->
          <div class="settings-card" v-if="settings.upload">
            <div class="card-header" style="margin-bottom: 24px; display: flex; align-items: center; gap: 8px; padding-bottom: 16px; border-bottom: 1px solid var(--border-light);">
               <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--accent-primary);">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                  <polyline points="13 2 13 9 20 9"></polyline>
               </svg>
               <h4 class="config-title" style="margin: 0; font-size: 16px;">{{ $t('admin.fileSettings') || 'File Settings' }}</h4>
            </div>

            <!-- File Size Limits -->
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.guestSizeLimit') }}</span>
                <span class="label-hint">{{ $t('admin.guestSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="guestFileSizeMB" type="number" class="form-input" min="1" max="1000" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.userSizeLimit') }}</span>
                <span class="label-hint">{{ $t('admin.userSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="userFileSizeMB" type="number" class="form-input" min="1" max="1000" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">VIP {{ $t('admin.userSizeLimit') }}</span>
                <span class="label-hint">VIP {{ $t('admin.userSizeLimitHint') }}</span>
              </label>
              <div class="input-group">
                <input v-model.number="vipFileSizeMB" type="number" class="form-input" min="1" max="5000" />
                <span class="input-group__suffix">MB</span>
              </div>
            </div>
            
            <div class="form-divider"></div>
            
            <!-- File Allowed Extensions -->
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.allowedFormats') }}</span>
                <span class="label-hint">{{ $t('admin.allowedFormatsHint') || 'Comma separated extensions' }}</span>
              </label>
              <input v-model="settings.upload.file_allowed_extensions" type="text" class="form-input" placeholder="zip,rar,7z,pdf,doc,docx..." />
            </div>

            <div class="form-divider"></div>
            
            <!-- File Rate Limits -->
            <h4 class="config-title">{{ $t('admin.fileRateLimits') }}</h4>
            
            <!-- Guest -->
            <h4 class="rate-limit-title">{{ $t('admin.guest') }}</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_file_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_file_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_guest_file_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>

            <div class="form-divider"></div>

            <!-- User -->
            <h4 class="rate-limit-title">{{ $t('admin.member') }}</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_file_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_file_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_user_file_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>

            <div class="form-divider"></div>

            <!-- VIP -->
            <h4 class="rate-limit-title">VIP</h4>
            <div class="form-row form-row--inline">
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perMinute') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_file_per_minute" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perHour') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_file_per_hour" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
              <div class="form-col">
                <label class="form-label">{{ $t('admin.perDay') }}</label>
                <div class="input-group">
                  <input v-model.number="settings.security.rate_limit_vip_file_per_day" type="number" class="form-input" />
                  <span class="input-group__suffix">{{ $t('admin.times') }}</span>
                </div>
              </div>
            </div>
            
          </div>
        </div>
        

        
        <!-- Storage Settings -->
        <div v-show="activeTab === 'storage'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.storage') }}</h3>
            <p class="section-desc">{{ $t('admin.storageSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.storage">
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.storageType') }}</span>
                <span class="label-hint">{{ $t('admin.storageTypeHint') }}</span>
              </label>
              <div class="radio-group">
                <label class="radio-item" :class="{ 'is-active': settings.storage.type === 'local' }">
                  <input type="radio" v-model="settings.storage.type" value="local" />
                  <span class="radio-item__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                  </span>
                  <span class="radio-item__text">{{ $t('admin.localStorage') }}</span>
                </label>
                <label class="radio-item" :class="{ 'is-active': settings.storage.type === 's3c' }">
                  <input type="radio" v-model="settings.storage.type" value="s3c" />
                  <span class="radio-item__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>
                    </svg>
                  </span>
                  <span class="radio-item__text">{{ $t('admin.s3Compatible') }}</span>
                </label>
                <label class="radio-item" :class="{ 'is-active': settings.storage.type === 'oss' }">
                  <input type="radio" v-model="settings.storage.type" value="oss" />
                  <span class="radio-item__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>
                    </svg>
                  </span>
                  <span class="radio-item__text">{{ $t('admin.aliOss') }}</span>
                </label>
                <label class="radio-item" :class="{ 'is-active': settings.storage.type === 'cos' }">
                  <input type="radio" v-model="settings.storage.type" value="cos" />
                  <span class="radio-item__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>
                    </svg>
                  </span>
                  <span class="radio-item__text">{{ $t('admin.tencentCos') }}</span>
                </label>
              </div>
            </div>
            
            <!-- Local Storage Config -->
            <template v-if="settings.storage.type === 'local'">
              <div class="form-divider"></div>
              <div class="config-section">
                <h4 class="config-title">{{ $t('admin.localStorageConfig') }}</h4>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.localPublicUrl') }}</span>
                    <span class="label-hint">{{ $t('admin.localPublicUrlHint') }}</span>
                  </label>
                  <input v-model="settings.storage.local_public_url" type="text" class="form-input" placeholder="https://cdn.example.com" />
                </div>
              </div>
            </template>
            
            <!-- S3 Compatible Config -->
            <template v-if="settings.storage.type === 's3c'">
              <div class="form-divider"></div>
              <div class="config-section">
                <h4 class="config-title">{{ $t('admin.s3cConfig') }}</h4>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.s3cProvider') }}</span>
                    <span class="label-hint">{{ $t('admin.s3cProviderHint') }}</span>
                  </label>
                  <select v-model="settings.storage.s3c_provider" class="form-input form-select" @change="onS3cProviderChange">
                    <option value="aws">AWS S3</option>
                    <option value="r2">Cloudflare R2</option>
                    <option value="cos">腾讯云 COS (S3模式)</option>
                    <option value="minio">MinIO</option>
                    <option value="b2">Backblaze B2</option>
                    <option value="spaces">DigitalOcean Spaces</option>
                    <option value="custom">{{ $t('admin.s3cCustom') }}</option>
                  </select>
                </div>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">{{ $t('admin.accessKeyId') }}</span></label>
                  <input v-model="settings.storage.s3c_access_key_id" type="text" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">{{ $t('admin.secretAccessKey') }}</span></label>
                  <input v-model="settings.storage.s3c_secret_access_key" type="password" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">{{ $t('admin.bucketName') }}</span></label>
                  <input v-model="settings.storage.s3c_bucket_name" type="text" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.s3cEndpoint') }}</span>
                    <span class="label-hint">{{ $t('admin.s3cEndpointHint') }}</span>
                  </label>
                  <input v-model="settings.storage.s3c_endpoint_url" type="text" class="form-input" :placeholder="s3cEndpointPlaceholder" />
                </div>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.region') }}</span>
                    <span class="label-hint">{{ $t('admin.s3cRegionHint') }}</span>
                  </label>
                  <input v-model="settings.storage.s3c_region" type="text" class="form-input" :placeholder="s3cRegionPlaceholder" />
                </div>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.publicUrl') }}</span>
                    <span class="label-hint">{{ $t('admin.s3cPublicUrlHint') }}</span>
                  </label>
                  <input v-model="settings.storage.s3c_public_url" type="text" class="form-input" placeholder="https://images.example.com" />
                </div>
              </div>
            </template>
            
            <!-- OSS Config -->
            <template v-if="settings.storage.type === 'oss'">
              <div class="form-divider"></div>
              <div class="config-section">
                <h4 class="config-title">{{ $t('admin.ossConfig') }}</h4>
                <p class="config-desc">{{ $t('admin.ossConfigDesc') }}</p>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">{{ $t('admin.accessKeyId') }}</span></label>
                  <input v-model="settings.storage.oss_access_key_id" type="text" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">{{ $t('admin.accessKeySecret') }}</span></label>
                  <input v-model="settings.storage.oss_access_key_secret" type="password" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">{{ $t('admin.bucketName') }}</span></label>
                  <input v-model="settings.storage.oss_bucket_name" type="text" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">{{ $t('admin.endpoint') }}</span></label>
                  <input v-model="settings.storage.oss_endpoint" type="text" class="form-input" placeholder="oss-cn-hangzhou.aliyuncs.com" />
                </div>
              </div>
            </template>
            
            <!-- COS Config -->
            <template v-if="settings.storage.type === 'cos'">
              <div class="form-divider"></div>
              <div class="config-section">
                <h4 class="config-title">{{ $t('admin.cosConfig') }}</h4>
                <p class="config-desc">{{ $t('admin.cosConfigDesc') }}</p>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">SecretId</span></label>
                  <input v-model="settings.storage.cos_secret_id" type="text" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label"><span class="label-text">SecretKey</span></label>
                  <input v-model="settings.storage.cos_secret_key" type="password" class="form-input" />
                </div>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.bucketName') }}</span>
                    <span class="label-hint">{{ $t('admin.cosBucketHint') }}</span>
                  </label>
                  <input v-model="settings.storage.cos_bucket_name" type="text" class="form-input" placeholder="mybucket-1250000000" />
                </div>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.region') }}</span>
                    <span class="label-hint">{{ $t('admin.cosRegionHint') }}</span>
                  </label>
                  <input v-model="settings.storage.cos_region" type="text" class="form-input" placeholder="ap-guangzhou" />
                </div>
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.publicUrl') }}</span>
                    <span class="label-hint">{{ $t('admin.cosPublicUrlHint') }}</span>
                  </label>
                  <input v-model="settings.storage.cos_public_url" type="text" class="form-input" placeholder="https://images.example.com" />
                </div>
              </div>
            </template>
          </div>
        </div>
        
        <!-- Audit Settings -->
        <div v-show="activeTab === 'audit'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.audit') }}</h3>
            <p class="section-desc">{{ $t('admin.auditSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.audit">
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableAudit') }}</span>
                <span class="label-hint">{{ $t('admin.enableAuditHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.audit.enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.audit.enabled">
              <div class="form-divider"></div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.auditProvider') }}</span>
                </label>
                <select v-model="settings.audit.provider" class="form-input form-select">
                  <option value="">{{ $t('admin.selectProvider') }}</option>
                  <option value="aliyun">{{ $t('admin.aliyunAudit') }}</option>
                  <option value="tencent">{{ $t('admin.tencentAudit') }}</option>
                </select>
              </div>
              
              <!-- 腾讯云提示 -->
              <div v-if="settings.audit.provider === 'tencent'" class="form-row">
                <el-alert type="info" :closable="false" show-icon>
                  {{ $t('admin.tencentAuditHint') }}
                </el-alert>
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.apiKey') }}</span>
                  <span class="label-hint" v-if="settings.audit.provider === 'aliyun'">{{ $t('admin.apiKeyHintAliyun') }}</span>
                  <span class="label-hint" v-else-if="settings.audit.provider === 'tencent'">{{ $t('admin.apiKeyHintTencent') }}</span>
                </label>
                <input v-model="settings.audit.api_key" type="text" class="form-input" />
              </div>
              
              <div class="form-row">
                <label class="form-label"><span class="label-text">{{ $t('admin.apiSecret') }}</span></label>
                <input v-model="settings.audit.api_secret" type="password" class="form-input" />
              </div>
              
              <!-- 腾讯云 COS Bucket 和 Region 配置 -->
              <template v-if="settings.audit.provider === 'tencent'">
                <div class="form-divider"></div>
                <h4 class="config-title">{{ $t('admin.tencentCosConfig') }}</h4>
                
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.tencentAuditBucket') }}</span>
                    <span class="label-hint">{{ $t('admin.tencentAuditBucketHint') }}</span>
                  </label>
                  <input v-model="settings.audit.tencent_bucket" type="text" class="form-input" placeholder="bucket-1250000000" />
                </div>
                
                <div class="form-row">
                  <label class="form-label">
                    <span class="label-text">{{ $t('admin.tencentAuditRegion') }}</span>
                    <span class="label-hint">{{ $t('admin.tencentAuditRegionHint') }}</span>
                  </label>
                  <input v-model="settings.audit.tencent_region" type="text" class="form-input" placeholder="ap-guangzhou" />
                </div>
              </template>
              
              <div class="form-divider"></div>
              
              <div class="form-row form-row--switch">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.autoReject') }}</span>
                  <span class="label-hint">{{ $t('admin.autoRejectHint') }}</span>
                </label>
                <label class="switch">
                  <input type="checkbox" v-model="settings.audit.auto_reject" />
                  <span class="switch__slider"></span>
                </label>
              </div>
              
              <div class="form-divider"></div>
              <h4 class="config-title">{{ $t('admin.violationImageHandling') }}</h4>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.violationImage') }}</span>
                  <span class="label-hint">{{ $t('admin.violationImageHint') }}</span>
                </label>
                <div class="logo-input-group">
                  <input v-model="settings.audit.violation_image" type="text" class="form-input" :placeholder="$t('admin.violationImagePlaceholder')" />
                  <div v-if="settings.audit.violation_image" class="logo-preview">
                    <img :src="settings.audit.violation_image" :alt="$t('admin.violationImagePreview')" @error="handleViolationImageError" />
                  </div>
                </div>
              </div>
              
            </template>
          </div>
        </div>
        
        <!-- Homepage Settings -->
        <div v-show="activeTab === 'home'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('admin.homeConfig') }}</h3>
            <p class="section-desc">{{ $t('admin.homeConfigDesc') }}</p>
          </div>
          
          <div class="settings-card">
            <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px;">
              {{ $t('admin.jsonConfigHint') }}
            </el-alert>

            <h4 class="config-title">{{ $t('admin.homeFeatures') }} (Array)</h4>
            <div class="form-row">
              <textarea v-model="settings.home.features" class="form-input form-textarea" rows="6" placeholder='[{"zh": "Feature", "en": "Feature"}]'></textarea>
            </div>

            <div class="form-divider"></div>
            <h4 class="config-title">{{ $t('admin.homeTableCols') }} (Object)</h4>
             <div class="form-row">
              <textarea v-model="settings.home.table_cols" class="form-input form-textarea" rows="4" placeholder='{"col_guest": {"zh": "...", "en": "..."}}'></textarea>
            </div>

            <div class="form-divider"></div>
            <h4 class="config-title">{{ $t('admin.homeTableRows') }} (Object)</h4>
            <div class="form-row">
              <textarea v-model="settings.home.table_rows" class="form-input form-textarea" rows="6" placeholder='{"row_single_file": {"zh": "...", "en": "..."}}'></textarea>
            </div>
          </div>
        </div>

        <!-- Email Settings -->
        <div v-show="activeTab === 'email'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.email') }}</h3>
            <p class="section-desc">{{ $t('admin.emailSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.email">
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableEmail') }}</span>
                <span class="label-hint">{{ $t('admin.enableEmailHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.email.enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.email.enabled">
              <div class="form-divider"></div>
              <h4 class="config-title">{{ $t('admin.smtpConfig') }}</h4>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.smtpHost') }}</span>
                  <span class="label-hint">{{ $t('admin.smtpHostHint') }}</span>
                </label>
                <input v-model="settings.email.smtp_host" type="text" class="form-input" :placeholder="$t('admin.smtpHostPlaceholder')" />
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.smtpPort') }}</span>
                  <span class="label-hint">{{ $t('admin.smtpPortHint') }}</span>
                </label>
                <input v-model.number="settings.email.smtp_port" type="number" class="form-input" :placeholder="$t('admin.smtpPortPlaceholder')" />
              </div>
              
              <div class="form-row form-row--switch">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.smtpSsl') }}</span>
                  <span class="label-hint">{{ $t('admin.smtpSslHint') }}</span>
                </label>
                <label class="switch">
                  <input type="checkbox" v-model="settings.email.smtp_ssl" />
                  <span class="switch__slider"></span>
                </label>
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.smtpUser') }}</span>
                  <span class="label-hint">{{ $t('admin.smtpUserHint') }}</span>
                </label>
                <input v-model="settings.email.smtp_user" type="text" class="form-input" :placeholder="$t('admin.smtpUserPlaceholder')" />
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.smtpPassword') }}</span>
                  <span class="label-hint">{{ $t('admin.smtpPasswordHint') }}</span>
                </label>
                <input v-model="settings.email.smtp_password" type="password" class="form-input" :placeholder="$t('admin.smtpPasswordPlaceholder')" />
              </div>
              
              <div class="form-divider"></div>
              <h4 class="config-title">{{ $t('admin.senderInfo') }}</h4>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.fromAddress') }}</span>
                  <span class="label-hint">{{ $t('admin.fromAddressHint') }}</span>
                </label>
                <input v-model="settings.email.from_address" type="email" class="form-input" :placeholder="$t('admin.fromAddressPlaceholder')" />
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.fromName') }}</span>
                  <span class="label-hint">{{ $t('admin.fromNameHint') }}</span>
                </label>
                <input v-model="settings.email.from_name" type="text" class="form-input" :placeholder="$t('admin.fromNamePlaceholder')" />
              </div>
              
              <div class="form-divider"></div>
              <h4 class="config-title">{{ $t('admin.connectionTest') }}</h4>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.testEmail') }}</span>
                  <span class="label-hint">{{ $t('admin.testEmailHint') }}</span>
                </label>
                <div class="test-email-group">
                  <input v-model="testEmail" type="email" class="form-input" :placeholder="$t('admin.testEmailPlaceholder')" />
                  <button class="btn btn--secondary" @click="sendTestEmail" :disabled="testingEmail">
                    <span v-if="testingEmail" class="btn-loader"></span>
                    {{ testingEmail ? $t('admin.sending') : $t('admin.sendTest') }}
                  </button>
                </div>
              </div>
              
              <div class="form-divider"></div>
              <h4 class="config-title">{{ $t('admin.emailTemplates') }}</h4>
              <p class="template-hint">{{ $t('admin.templateVariables') }}：<code v-pre>{{site_name}}</code> <code v-pre>{{username}}</code> <code v-pre>{{verify_url}}</code> <code v-pre>{{reset_url}}</code></p>
              
              <div class="template-cards">
                <div class="template-card">
                  <div class="template-card__header">
                    <span class="template-card__title">📧 {{ $t('admin.emailVerification') }}</span>
                    <div class="template-card__actions">
                      <button class="btn btn--text btn--sm" @click="openTemplateEditor('verify')">{{ $t('admin.editTemplate') }}</button>
                      <button class="btn btn--text btn--sm" @click="resetTemplate('verify')">{{ $t('admin.resetTemplate') }}</button>
                    </div>
                  </div>
                  <div class="template-card__preview">
                    <div class="preview-label">{{ $t('admin.templateSubject') }}：</div>
                    <div class="preview-value">{{ settings.email.template_verify_subject }}</div>
                  </div>
                </div>
                
                <div class="template-card">
                  <div class="template-card__header">
                    <span class="template-card__title">🔑 {{ $t('admin.passwordReset') }}</span>
                    <div class="template-card__actions">
                      <button class="btn btn--text btn--sm" @click="openTemplateEditor('reset')">{{ $t('admin.editTemplate') }}</button>
                      <button class="btn btn--text btn--sm" @click="resetTemplate('reset')">{{ $t('admin.resetTemplate') }}</button>
                    </div>
                  </div>
                  <div class="template-card__preview">
                    <div class="preview-label">{{ $t('admin.templateSubject') }}：</div>
                    <div class="preview-value">{{ settings.email.template_reset_subject }}</div>
                  </div>
                </div>
              </div>
              
            </template>
          </div>
        </div>
        
        <!-- Payment Settings -->
        <div v-show="activeTab === 'payment'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.payment') }}</h3>
            <p class="section-desc">{{ $t('admin.paymentSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.payment">
            <h4 class="config-title">Stripe</h4>
            
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableStripe') }}</span>
                <span class="label-hint">{{ $t('admin.enableStripeHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.payment.stripe_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.payment.stripe_enabled">
              <div class="form-divider"></div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.stripeSecretKey') }}</span>
                </label>
                <input v-model="settings.payment.stripe_secret_key" type="password" class="form-input" />
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.stripeWebhookSecret') }}</span>
                </label>
                <input v-model="settings.payment.stripe_webhook_secret" type="password" class="form-input" />
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.stripeCurrency') }}</span>
                  <span class="label-hint">{{ $t('admin.stripeCurrencyHint') }}</span>
                </label>
                <input v-model="settings.payment.stripe_currency" type="text" class="form-input" placeholder="HKD" />
              </div>
            </template>
            
            <!-- Alipay Section -->
            <div class="form-divider"></div>
            <h4 class="config-title">Alipay (当面付)</h4>
            
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">Enable Alipay</span>
                <span class="label-hint">Enable Alipay Face-to-Face Payment</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.payment.alipay_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.payment.alipay_enabled">
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">App ID</span>
                </label>
                <input v-model="settings.payment.alipay_app_id" type="text" class="form-input" />
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">Alipay Private Key</span>
                  <span class="label-hint">应用私钥 (RSA2)</span>
                </label>
                <textarea v-model="settings.payment.alipay_private_key" class="form-input form-textarea" rows="3" placeholder="-----BEGIN RSA PRIVATE KEY-----..."></textarea>
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">Alipay Public Key</span>
                  <span class="label-hint">支付宝公钥 (不是应用公钥)</span>
                </label>
                <textarea v-model="settings.payment.alipay_public_key" class="form-input form-textarea" rows="4" placeholder="-----BEGIN PUBLIC KEY-----..."></textarea>
              </div>
            </template>

            <!-- VIP Plans Section -->
            <div class="form-divider"></div>
            <h4 class="config-title">{{ $t('settings.vipPlansConfig') }}</h4>
            <p class="section-desc">{{ $t('settings.vipPlansDesc') }}</p>

            <div class="plans-grid">
              <!-- Month -->
              <div class="plan-card">
                <div class="plan-header">
                  <h5>{{ $t('settings.planMonthly') }}</h5>
                  <label class="switch switch--sm">
                    <input type="checkbox" v-model="settings.payment.vip_month_enabled" />
                    <span class="switch__slider"></span>
                  </label>
                </div>
                <div class="plan-body" v-if="settings.payment.vip_month_enabled">
                   <div class="form-row compact">
                     <label>{{ $t('settings.planPrice') }}</label>
                     <input v-model="settings.payment.vip_month_price" type="text" class="form-input" />
                   </div>
                   <div class="form-row compact">
                     <label>{{ $t('settings.planStripeId') }}</label>
                     <input v-model="settings.payment.vip_month_stripe_id" type="text" class="form-input" />
                   </div>
                </div>
              </div>

              <!-- Quarter -->
              <div class="plan-card">
                <div class="plan-header">
                  <h5>{{ $t('settings.planQuarterly') }}</h5>
                  <label class="switch switch--sm">
                    <input type="checkbox" v-model="settings.payment.vip_quarter_enabled" />
                    <span class="switch__slider"></span>
                  </label>
                </div>
                <div class="plan-body" v-if="settings.payment.vip_quarter_enabled">
                   <div class="form-row compact">
                     <label>{{ $t('settings.planPrice') }}</label>
                     <input v-model="settings.payment.vip_quarter_price" type="text" class="form-input" />
                   </div>
                   <div class="form-row compact">
                     <label>{{ $t('settings.planStripeId') }}</label>
                     <input v-model="settings.payment.vip_quarter_stripe_id" type="text" class="form-input" />
                   </div>
                </div>
              </div>

              <!-- Year -->
              <div class="plan-card">
                <div class="plan-header">
                  <h5>{{ $t('settings.planYearly') }}</h5>
                  <label class="switch switch--sm">
                    <input type="checkbox" v-model="settings.payment.vip_year_enabled" />
                    <span class="switch__slider"></span>
                  </label>
                </div>
                <div class="plan-body" v-if="settings.payment.vip_year_enabled">
                   <div class="form-row compact">
                     <label>{{ $t('settings.planPrice') }}</label>
                     <input v-model="settings.payment.vip_year_price" type="text" class="form-input" />
                   </div>
                   <div class="form-row compact">
                     <label>{{ $t('settings.planStripeId') }}</label>
                     <input v-model="settings.payment.vip_year_stripe_id" type="text" class="form-input" />
                   </div>
                </div>
              </div>

              <!-- Forever -->
              <div class="plan-card">
                <div class="plan-header">
                  <h5>{{ $t('settings.planLifetime') }}</h5>
                  <label class="switch switch--sm">
                    <input type="checkbox" v-model="settings.payment.vip_forever_enabled" />
                    <span class="switch__slider"></span>
                  </label>
                </div>
                <div class="plan-body" v-if="settings.payment.vip_forever_enabled">
                   <div class="form-row compact">
                     <label>{{ $t('settings.planPrice') }}</label>
                     <input v-model="settings.payment.vip_forever_price" type="text" class="form-input" />
                   </div>
                   <div class="form-row compact">
                     <label>{{ $t('settings.planStripeId') }}</label>
                     <input v-model="settings.payment.vip_forever_stripe_id" type="text" class="form-input" />
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Announcement Settings -->
        <div v-show="activeTab === 'announcement'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.announcement') }}</h3>
            <p class="section-desc">{{ $t('admin.announcementSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.announcement">
            <!-- Popup Announcement -->
            <h4 class="config-title">{{ $t('admin.popupAnnouncement') }}</h4>
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enablePopup') }}</span>
                <span class="label-hint">{{ $t('admin.enablePopupHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.announcement.popup_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.announcement.popup_enabled">
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.popupContent') }}</span>
                  <span class="label-hint">{{ $t('admin.popupContentHint') }}</span>
                </label>
                <textarea 
                  v-model="settings.announcement.popup_content" 
                  class="form-input form-textarea" 
                  rows="6"
                  :placeholder="$t('admin.popupContentHint')"
                ></textarea>
              </div>
            </template>
            
            <div class="form-divider"></div>
            
            <!-- Navbar Announcement -->
            <h4 class="config-title">{{ $t('admin.navbarAnnouncement') }}</h4>
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableNavbar') }}</span>
                <span class="label-hint">{{ $t('admin.enableNavbarHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.announcement.navbar_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.announcement.navbar_enabled">
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.navbarContent') }}</span>
                  <span class="label-hint">{{ $t('admin.navbarContentHint') }}</span>
                </label>
                <input 
                  v-model="settings.announcement.navbar_content" 
                  type="text" 
                  class="form-input" 
                  :placeholder="$t('admin.navbarContentHint')"
                />
              </div>
            </template>
          </div>
        </div>

        <!-- Template Editor Modal -->
        <div v-if="editingTemplate" class="modal-overlay" @click.self="closeTemplateEditor">
          <div class="modal-content template-editor">
            <div class="modal-header">
              <h3>{{ editingTemplate === 'verify' ? $t('admin.editVerifyTemplate') : $t('admin.editResetTemplate') }}</h3>
              <button class="modal-close" @click="closeTemplateEditor">&times;</button>
            </div>
            <div class="modal-body">
              <div class="form-row" style="grid-template-columns: 1fr;">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.emailSubject') }}</span>
                </label>
                <input 
                  v-model="settings.email[`template_${editingTemplate}_subject`]" 
                  type="text" 
                  class="form-input" 
                />
              </div>
              <div class="form-row" style="grid-template-columns: 1fr; margin-top: 16px;">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.emailBody') }}</span>
                  <span class="label-hint">{{ $t('admin.emailBodyHint') }}</span>
                </label>
                <textarea 
                  v-model="settings.email[`template_${editingTemplate}_body`]" 
                  class="form-input form-textarea template-textarea"
                  rows="15"
                ></textarea>
              </div>
              <div class="variable-hints">
                <span class="hint-title">{{ $t('admin.templateVariables') }}：</span>
                <code v-pre>{{site_name}}</code> - {{ $t('settings.siteName') }}
                <code v-pre>{{username}}</code> - {{ $t('auth.username') }}
                <template v-if="editingTemplate === 'verify'">
                  <code v-pre>{{verify_url}}</code> - {{ $t('admin.verifyUrl') }}
                </template>
                <template v-else>
                  <code v-pre>{{reset_url}}</code> - {{ $t('admin.resetUrl') }}
                </template>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn--secondary" @click="closeTemplateEditor">{{ $t('common.close') }}</button>
            </div>
          </div>
        </div>
        

        <!-- CDN Settings -->
        <div v-show="activeTab === 'cdn'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('settings.cdn') }}</h3>
            <p class="section-desc">{{ $t('admin.cdnSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.cdn">
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.cfPurgeEnabled') }}</span>
                <span class="label-hint">{{ $t('admin.cfPurgeEnabledHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.cdn.cf_purge_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.cdn.cf_purge_enabled">
              <div class="form-divider"></div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.cfApiToken') }}</span>
                  <span class="label-hint">{{ $t('admin.cfApiTokenHint') }}</span>
                </label>
                <input v-model="settings.cdn.cf_api_token" type="password" class="form-input" placeholder="Cloudflare API Token" />
              </div>
              
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.cfZoneId') }}</span>
                  <span class="label-hint">{{ $t('admin.cfZoneIdHint') }}</span>
                </label>
                <input v-model="settings.cdn.cf_zone_id" type="text" class="form-input" placeholder="Cloudflare Zone ID" />
              </div>

              <div class="form-info-box">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                <p>{{ $t('admin.cfPurgeInfo') }}</p>
              </div>
            </template>
          </div>
        </div>

        <div v-show="activeTab === 'ai'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('admin.aiSettings') }}</h3>
            <p class="section-desc">{{ $t('admin.configureAiModels') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.ai">
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableAiAnalysis') }}</span>
                <span class="label-hint">{{ $t('admin.enableAiAnalysisHint') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.ai.analysis_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>

            <div class="form-divider"></div>
            <h4 class="config-title">Google Gemini</h4>
            
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.geminiApiKeys') }}</span>
                <span class="label-hint">{{ $t('admin.geminiApiKeysHint') }}</span>
              </label>
              <textarea 
                v-model="settings.ai.gemini_api_keys" 
                class="form-input form-textarea" 
                rows="3" 
                placeholder="AIzaSy..., AIzaSy..."
              ></textarea>
            </div>
            
            <div class="form-info-box" style="margin-top: 16px;">
               <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
               <p>{{ $t('admin.freeTierLimit') }}</p>
            </div>
          </div>
        </div>

        <!-- OAuth Settings -->
        <div v-show="activeTab === 'oauth'" class="settings-section">
          <div class="section-header">
            <h3 class="section-title">{{ $t('admin.oauth') }}</h3>
            <p class="section-desc">{{ $t('admin.oauthSettingsDesc') }}</p>
          </div>
          
          <div class="settings-card" v-if="settings.oauth">
            <!-- Google OAuth -->
            <h4 class="config-title">Google OAuth 2.0</h4>
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableGoogle') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.oauth.google_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.oauth.google_enabled">
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.googleClientId') }}</span>
                </label>
                <input v-model="settings.oauth.google_client_id" type="text" class="form-input" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.googleClientSecret') }}</span>
                </label>
                <input v-model="settings.oauth.google_client_secret" type="password" class="form-input" />
              </div>
            </template>

            <div class="form-divider"></div>

            <!-- Linux.do OAuth -->
            <h4 class="config-title">Linux.do OAuth 2.0</h4>
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.enableLinuxdo') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.oauth.linuxdo_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.oauth.linuxdo_enabled">
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.linuxdoClientId') }}</span>
                </label>
                <input v-model="settings.oauth.linuxdo_client_id" type="text" class="form-input" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.linuxdoClientSecret') }}</span>
                </label>
                <input v-model="settings.oauth.linuxdo_client_secret" type="password" class="form-input" />
              </div>
            </template>

            <div class="form-divider"></div>

            <!-- GitHub OAuth -->
            <h4 class="config-title">GitHub OAuth 2.0</h4>
            <div class="form-row form-row--switch">
              <label class="form-label">
                <span class="label-text">{{ $t('admin.github_enabled') }}</span>
              </label>
              <label class="switch">
                <input type="checkbox" v-model="settings.oauth.github_enabled" />
                <span class="switch__slider"></span>
              </label>
            </div>
            
            <template v-if="settings.oauth.github_enabled">
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.github_client_id') }}</span>
                </label>
                <input v-model="settings.oauth.github_client_id" type="text" class="form-input" />
              </div>
              <div class="form-row">
                <label class="form-label">
                  <span class="label-text">{{ $t('admin.github_client_secret') }}</span>
                </label>
                <input v-model="settings.oauth.github_client_secret" type="password" class="form-input" />
              </div>
            </template>
          </div>
        </div>

        <!-- Save Button -->
        <div class="settings-actions">
          <button class="btn btn--primary btn--lg" @click="saveSettings" :disabled="saving">
            <svg v-if="!saving" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17,21 17,13 7,13 7,21"/><polyline points="7,3 7,8 15,8"/>
            </svg>
            <span v-if="saving" class="btn-loader"></span>
            {{ saving ? $t('admin.saving') : $t('admin.saveChanges') }}
          </button>
          <span class="save-hint">{{ $t('admin.saveHint') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useThemeStore } from '@/stores/theme'

const { t } = useI18n()

const activeTab = ref('general')
const isMenuOpen = ref(false)
const saving = ref(false)
const themeStore = useThemeStore()

const selectTab = (key) => {
  activeTab.value = key
  isMenuOpen.value = false
}

// Check for hash in URL to switch tab
onMounted(() => {
  loadSettings()
  const hash = window.location.hash.substring(1)
  if (hash && tabs.value.some(tab => tab.key === hash)) {
    activeTab.value = hash
  }
})

const tabs = computed(() => [
  { key: 'general', label: t('settings.general'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>' },
  { key: 'appearance', label: t('settings.appearance'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>' },
  { key: 'cdn', label: t('settings.cdn'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M19.07 4.93L4.93 19.07"/></svg>' },
  { key: 'cs', label: t('settings.cs'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>' },
  { key: 'upload', label: t('settings.upload'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17,8 12,3 7,8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>' },
  { key: 'storage', label: t('settings.storage'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>' },
  { key: 'audit', label: t('settings.audit'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/><path d="M12 8v4l3 3"/></svg>' },
  { key: 'home', label: t('admin.homeConfig'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>' },
  { key: 'email', label: t('settings.email'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>' },
  { key: 'payment', label: t('settings.payment'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>' },
  { key: 'oauth', label: t('admin.oauth'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><circle cx="12" cy="12" r="3"/></svg>' },
  { key: 'announcement', label: t('settings.announcement'), icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>' },
  { key: 'ai', label: 'AI Settings', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/><path d="M12 6v6l4 2"/></svg>' },
])

const settings = reactive({
  general: { 
    site_name: '', site_title: '', site_description: '', site_slogan: '', site_footer: '', site_url: '',
    site_logo: '', site_logo_dark: '', site_favicon: '', timezone: 'Asia/Shanghai',
    enable_registration: true, enable_guest_upload: true 
  },
  appearance: { theme_mode: 'light' },
  cs: { mode: 'off', crisp_id: '', custom_title: '', custom_qr: '', custom_desc: '', custom_link: '', custom_link_text: '' },
// ... (settings reactive object)
  upload: { 
    max_size_guest: 5242880, max_size_user: 10485760, max_size_vip: 52428800, 
    allowed_extensions: 'png,jpg,jpeg,gif,webp', compression_quality: 85, max_dimension: 0,
    
    // File Settings
    file_max_size_guest: 52428800, file_max_size_user: 104857600, file_max_size_vip: 524288000,
    file_allowed_extensions: 'zip,rar,7z,tar,gz,pdf,doc,docx,xls,xlsx,ppt,pptx,txt,md',
    
    // Video Size Settings
    video_max_size_guest: 20971520, video_max_size_user: 104857600, video_max_size_vip: 2147483648,
    video_allowed_extensions: 'mp4,webm,ogg,mov,mkv',
  },
  // Security settings (reuse upload object or create new? Since keys are security_... let's check backend)
  // Backend keys: security_rate_limit_...
  // The loadSettings function maps category_key. 
  // Wait, in settings.py defaults: "security_rate_limit_..."
  // So category is "security". But I don't have a "security" tab or object in settings reactive.
  // I should add a security object.
  security: {
    rate_limit_guest_per_minute: 3, rate_limit_guest_per_hour: 10, rate_limit_guest_per_day: 30,
    rate_limit_user_per_minute: 10, rate_limit_user_per_hour: 100, rate_limit_user_per_day: 500,
    rate_limit_vip_per_minute: 30, rate_limit_vip_per_hour: 300, rate_limit_vip_per_day: 2000,
    
    // Video Limits (New Standard)
    rate_limit_guest_video_per_minute: 3, rate_limit_guest_video_per_hour: 10, rate_limit_guest_video_per_day: 30,
    rate_limit_user_video_per_minute: 10, rate_limit_user_video_per_hour: 50, rate_limit_user_video_per_day: 100,
    rate_limit_vip_video_per_minute: 30, rate_limit_vip_video_per_hour: 100, rate_limit_vip_video_per_day: 500,

    // File Limits
    rate_limit_guest_file_per_minute: 1, rate_limit_guest_file_per_hour: 3, rate_limit_guest_file_per_day: 10,
    rate_limit_user_file_per_minute: 5, rate_limit_user_file_per_hour: 20, rate_limit_user_file_per_day: 50,
    rate_limit_vip_file_per_minute: 10, rate_limit_vip_file_per_hour: 50, rate_limit_vip_file_per_day: 200,
    
    auto_ban_enabled: true, audit_fail_threshold: 3, rate_exceed_threshold: 3, temp_ban_duration: 1440,
    rate_limit_login_attempts: 5, real_ip_header: 'X-Forwarded-For', trust_proxy: true,
    auth_provider: 'both'
  },
  storage: { 
    type: 'local', local_public_url: '',
    s3c_provider: 'custom', s3c_access_key_id: '', s3c_secret_access_key: '', s3c_bucket_name: '', s3c_endpoint_url: '', s3c_region: '', s3c_public_url: '',
    oss_access_key_id: '', oss_access_key_secret: '', oss_bucket_name: '', oss_endpoint: '',
    cos_secret_id: '', cos_secret_key: '', cos_bucket_name: '', cos_region: '', cos_public_url: '',
  },
  audit: { enabled: false, provider: '', api_key: '', api_secret: '', auto_reject: false, violation_image: '', tencent_bucket: '', tencent_region: '' },
  email: { 
    enabled: false, smtp_host: '', smtp_port: 587, smtp_user: '', smtp_password: '', smtp_ssl: false,
    from_address: '', from_name: 'PicKoala',
    template_verify_subject: '', template_verify_body: '', template_reset_subject: '', template_reset_body: ''
  },
  payment: {
    stripe_enabled: false, stripe_secret_key: '', stripe_webhook_secret: '', stripe_currency: 'HKD',
    alipay_enabled: false, alipay_app_id: '', alipay_private_key: '', alipay_public_key: '',
    vip_month_enabled: true, vip_month_price: '9.99', vip_month_stripe_id: '',
    vip_quarter_enabled: false, vip_quarter_price: '29.99', vip_quarter_stripe_id: '',
    vip_year_enabled: true, vip_year_price: '99.99', vip_year_stripe_id: '',
    vip_forever_enabled: false, vip_forever_price: '299.99', vip_forever_stripe_id: '',
  },
  announcement: {
    popup_enabled: false, popup_content: '',
    navbar_enabled: false, navbar_content: ''
  },
  casdoor: {
    enabled: false, endpoint: '', client_id: '', client_secret: '',
    certificate: '', org_name: '', app_name: ''
  },
  oauth: {
    google_enabled: false, google_client_id: '', google_client_secret: '',
    linuxdo_enabled: false, linuxdo_client_id: '', linuxdo_client_secret: ''
  },
  home: {
    features: '[]',
    table_cols: '{}',
    table_rows: '{}'
  },
  cdn: {
    cf_purge_enabled: false,
    cf_api_token: '',
    cf_zone_id: ''
  },
  ai: {
    gemini_api_keys: '',
    analysis_enabled: false
  }
})

// Sync preview
watch(() => settings.appearance?.theme_mode, (val) => {
  if (val) themeStore.setTheme(val)
})

// Email test
const testEmail = ref('')
const testingEmail = ref(false)
const editingTemplate = ref(null)

const guestSizeMB = computed({
  get: () => Math.round(settings.upload.max_size_guest / 1048576),
  set: (v) => { settings.upload.max_size_guest = v * 1048576 }
})

const userSizeMB = computed({
  get: () => Math.round(settings.upload.max_size_user / 1048576),
  set: (v) => { settings.upload.max_size_user = v * 1048576 }
})

const vipSizeMB = computed({
  get: () => Math.round(settings.upload.max_size_vip / 1048576),
  set: (v) => { settings.upload.max_size_vip = v * 1048576 }
})

const guestFileSizeMB = computed({
  get: () => Math.round(settings.upload.file_max_size_guest / 1048576),
  set: (v) => { settings.upload.file_max_size_guest = v * 1048576 }
})

const userFileSizeMB = computed({
  get: () => Math.round(settings.upload.file_max_size_user / 1048576),
  set: (v) => { settings.upload.file_max_size_user = v * 1048576 }
})

const vipFileSizeMB = computed({
  get: () => Math.round(settings.upload.file_max_size_vip / 1048576),
  set: (v) => { settings.upload.file_max_size_vip = v * 1048576 }
})

const guestVideoSizeMB = computed({
  get: () => Math.round(settings.upload.video_max_size_guest / 1048576),
  set: (v) => { settings.upload.video_max_size_guest = v * 1048576 }
})

const userVideoSizeMB = computed({
  get: () => Math.round(settings.upload.video_max_size_user / 1048576),
  set: (v) => { settings.upload.video_max_size_user = v * 1048576 }
})

const vipVideoSizeMB = computed({
  get: () => Math.round(settings.upload.video_max_size_vip / 1048576),
  set: (v) => { settings.upload.video_max_size_vip = v * 1048576 }
})

const s3cEndpointPlaceholder = computed(() => {
  const provider = settings.storage.s3c_provider
  const placeholders = {
    'aws': '留空使用默认AWS端点',
    'r2': 'https://<account_id>.r2.cloudflarestorage.com',
    'cos': 'https://cos.<region>.myqcloud.com',
    'minio': 'https://minio.example.com:9000',
    'b2': 'https://s3.<region>.backblazeb2.com',
    'spaces': 'https://<region>.digitaloceanspaces.com',
    'custom': 'https://s3.example.com',
  }
  return placeholders[provider] || placeholders['custom']
})

const s3cRegionPlaceholder = computed(() => {
  const provider = settings.storage.s3c_provider
  const placeholders = {
    'aws': 'us-east-1', 'r2': 'auto', 'cos': 'ap-guangzhou', 'minio': 'us-east-1',
    'b2': 'us-west-004', 'spaces': 'nyc3', 'custom': 'us-east-1',
  }
  return placeholders[provider] || placeholders['custom']
})

const onS3cProviderChange = () => {
  if (settings.storage.s3c_provider === 'r2' && !settings.storage.s3c_region) {
    settings.storage.s3c_region = 'auto'
  }
}

const loadSettings = async () => {
  try {
    const response = await api.get('/admin/settings')
    for (const group of response.data) {
      if (!settings[group.category]) continue
      for (const setting of group.settings) {
        const key = setting.key.replace(`${group.category}_`, '')
        let value = setting.value ?? ''
        if (value === 'true') value = true
        else if (value === 'false') value = false
        else if (typeof value === 'string' && /^\d+$/.test(value)) value = parseInt(value)
        if (key in settings[group.category]) {
          settings[group.category][key] = value
        }
      }
    }
  } catch (error) {
    console.error(error)
  }
}

const handleLogoError = (e) => { e.target.style.display = 'none' }
const handleLogoDarkError = (e) => { e.target.style.display = 'none' }
const handleFaviconError = (e) => { e.target.style.display = 'none' }
const handleViolationImageError = (e) => { e.target.style.display = 'none' }

const sendTestEmail = async () => {
  if (!testEmail.value) {
    ElMessage.warning(t('admin.testEmailHint'))
    return
  }
  testingEmail.value = true
  try {
    const response = await api.post('/admin/settings/email/test', { to_email: testEmail.value })
    ElMessage.success(response.data.message || t('common.success'))
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || t('error.submitFailed'))
  } finally {
    testingEmail.value = false
  }
}

const openTemplateEditor = (type) => { editingTemplate.value = type }
const closeTemplateEditor = () => { editingTemplate.value = null }
const resetTemplate = (type) => {
  // Simple defaults or fetch from network if needed. For now assume safe placeholders or empty.
  ElMessage.success(t('common.success'))
}


const handleCertificateUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    if (settings.value.casdoor) {
      settings.value.casdoor.certificate = e.target.result
      ElMessage.success(t('admin.certificateUploaded'))
    }
  }
  reader.onerror = () => {
    ElMessage.error(t('error.uploadFailed'))
  }
  reader.readAsText(file)
}

const saveSettings = async () => {

  saving.value = true
  try {
    const payload = {}
    for (const [category, categorySettings] of Object.entries(settings)) {
      for (const [key, value] of Object.entries(categorySettings)) {
        payload[`${category}_${key}`] = String(value)
      }
    }
    await api.post('/admin/settings/batch', payload)
    ElMessage.success(t('settings.saveSuccess'))
  } catch (error) {
    console.error(error)
    ElMessage.error(t('error.saveFailed'))
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.admin-page {
  max-width: 100%;
  margin: 0;
  padding: 24px;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.admin-menu-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  padding: 8px;
  cursor: pointer;
}

.admin-page__title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.settings-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 24px;
}

// Sidebar Navigation
.settings-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: sticky;
  top: 88px;
  align-self: start;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  padding-right: 4px;
  
  /* Modern scrollbar */
  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--border-light);
    border-radius: 2px;
  }
  &:hover::-webkit-scrollbar-thumb {
    background: var(--border-medium);
  }
  
  &__item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.15s;
    text-align: left;
    
    &:hover {
      color: var(--text-primary);
      background: var(--bg-secondary);
    }
    
    &.is-active {
      color: var(--text-primary);
      background: var(--bg-card);
      box-shadow: var(--shadow-sm);
    }
  }
  
  &__icon {
    display: flex;
    color: inherit;
    opacity: 0.7;
  }
}

// Settings Content
.settings-content {
  min-width: 0;
}

.settings-section {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-header {
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.section-desc {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

.settings-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-neu-flat);
}

// Form Styles
.form-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 16px;
  align-items: start;
  margin-bottom: 20px;
  
  &:last-child { margin-bottom: 0; }
  
  &--switch {
    align-items: center;
  }
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.label-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.label-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px var(--accent-primary-alpha);
  }
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='%23666'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-divider {
  height: 1px;
  background: var(--border-light);
  margin: 24px 0;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
  
  .form-input {
    padding-right: 40px;
  }
  
  &__suffix {
    position: absolute;
    right: 12px;
    font-size: 13px;
    color: var(--text-tertiary);
    pointer-events: none;
  }
}

// Radio Group
.radio-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  
  input {
    display: none;
  }
  
  &__icon {
    display: flex;
    color: var(--text-tertiary);
  }
  
  &__text {
    font-size: 14px;
    color: var(--text-secondary);
  }
  
  &:hover {
    border-color: var(--border-medium);
    background: var(--bg-secondary);
  }
  
  &.is-active {
    border-color: var(--accent-primary);
    background: var(--accent-primary-alpha);
    
    .radio-item__icon,
    .radio-item__text {
      color: var(--accent-primary);
    }
  }
}

// Logo Input
.logo-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.logo-preview {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  
  img {
    max-width: 200px;
    max-height: 60px;
    object-fit: contain;
  }
  
  &--dark {
    background: #1a1a1a;
  }
}

.favicon-preview {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  
  img {
    width: 32px;
    height: 32px;
    object-fit: contain;
  }
}

.config-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 16px;
}

.config-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin: -12px 0 16px;
}

.slider-input {
  display: flex;
  align-items: center;
  gap: 16px;
  
  .slider {
    flex: 1;
    max-width: 300px;
    height: 6px;
    appearance: none;
    background: var(--bg-tertiary);
    border-radius: 3px;
    
    &::-webkit-slider-thumb {
      appearance: none;
      width: 18px;
      height: 18px;
      background: var(--accent-primary);
      border-radius: 50%;
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
  }
  
  .slider-value {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    min-width: 48px;
  }
}

// Switch
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
    
    &:checked + .switch__slider {
      background: var(--accent-primary);
      &::before { transform: translateX(20px); }
    }
  }
  
  &__slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--bg-tertiary);
    border-radius: 24px;
    transition: .3s;
    
    &::before {
      position: absolute;
      content: "";
      height: 20px;
      width: 20px;
      left: 2px;
      bottom: 2px;
      background-color: white;
      border-radius: 50%;
      transition: .3s;
    }
  }
  
  &--sm {
    width: 36px;
    height: 20px;
    
    .switch__slider::before {
      height: 16px;
      width: 16px;
    }
    
    input:checked + .switch__slider::before {
      transform: translateX(16px);
    }
  }
}

// File Upload
.file-upload {
  position: relative;
  overflow: hidden;
  
  input[type="file"] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
  }
  
  &__btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      border-color: var(--border-medium);
      color: var(--text-primary);
    }
  }
}

// Tags
.tag {
  display: inline-flex;
  padding: 4px 8px;
  background: var(--accent-primary-alpha);
  color: var(--accent-primary);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  
  &--success {
    background: rgba(16, 185, 129, 0.1);
    color: #10B981;
  }
  
  &--warning {
    background: rgba(245, 158, 11, 0.1);
    color: #F59E0B;
  }
  
  &--danger {
    background: rgba(239, 68, 68, 0.1);
    color: #EF4444;
  }
}

// User Info Group
.user-info-group {
  display: flex;
  align-items: center;
  gap: 12px;
  
  &__avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  &__details {
    display: flex;
    flex-direction: column;
    
    .name {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-primary);
    }
    
    .email {
      font-size: 12px;
      color: var(--text-tertiary);
    }
  }
}

// Config Section
.config-section {
  margin-top: 8px;
}

// Actions
.settings-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--border-light);
}

.save-hint {
  font-size: 13px;
  color: var(--text-tertiary);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  
  &--primary {
    background: var(--accent-primary);
    color: var(--text-inverse);
    &:hover { opacity: 0.9; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }
  
  &--lg {
    padding: 14px 28px;
    font-size: 15px;
  }
}

.btn-loader {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.btn--secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  &:hover { background: var(--bg-tertiary); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.btn--text {
  background: transparent;
  color: var(--accent-primary);
  padding: 6px 12px;
  &:hover { background: var(--bg-secondary); }
}

.btn--sm {
  padding: 6px 12px;
  font-size: 13px;
}

// Email Settings
.test-email-group {
  display: flex;
  gap: 12px;
  
  .form-input {
    flex: 1;
  }
  
  .btn {
    flex-shrink: 0;
  }
}

.template-hint {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: -8px 0 16px;
  
  code {
    background: var(--bg-secondary);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    margin: 0 2px;
  }
}

.template-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.template-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 16px;
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  &__title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  &__actions {
    display: flex;
    gap: 4px;
  }
  
  &__preview {
    display: flex;
    gap: 8px;
    font-size: 13px;
  }
  
  .preview-label {
    color: var(--text-tertiary);
    flex-shrink: 0;
  }
  
  .preview-value {
    color: var(--text-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

// Payment Plans Grid
.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.plan-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 16px;
  border: 1px solid var(--border-light);
  
  .plan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    h5 {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
  }
  
  .plan-body {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-light);
  }
  
  .form-row.compact {
    margin-bottom: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    label {
      font-size: 12px;
      color: var(--text-tertiary);
    }
    
    input {
      font-size: 13px;
      padding: 6px 10px;
      height: 32px;
    }
  }
}

// Modal
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-light);
  
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0;
  line-height: 1;
  
  &:hover {
    color: var(--text-primary);
  }
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.template-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  min-height: 300px;
}

.variable-hints {
  margin-top: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  font-size: 12px;
  color: var(--text-tertiary);
  
  .hint-title {
    font-weight: 600;
    margin-right: 8px;
  }
  
  code {
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 4px;
    margin: 0 4px;
    color: var(--text-secondary);
  }
}

.form-row--inline {
  display: flex;
  gap: 16px;
}

.form-col {
  flex: 1;
  min-width: 0;
}

.rate-limit-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px 0;
}

// Responsive
@media (max-width: 768px) {

  .admin-page {
    padding: 16px;
  }

  .admin-menu-toggle {
    display: block;
  }

  .settings-layout {
    display: block; // Stack layout
  }

  .settings-nav-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 99;
    animation: fadeIn 0.3s;
  }

  .settings-nav {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    width: 280px;
    background: var(--bg-card);
    z-index: 100;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.2);
    padding: 24px 0;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &.is-open {
      transform: translateX(0);
    }
    
    &__item {
      border-radius: 0;
      margin: 4px 0;
      padding-left: 24px;
    }
  }

  .settings-content {
    margin-left: 0;
  }
  

}
</style>
