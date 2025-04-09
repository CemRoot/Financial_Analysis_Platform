let inactivityTimer;
let warningTimer;

// Set the timeout durations (in milliseconds)
const TIMEOUT_DURATION = 15 * 60 * 1000; // 15 minutes
const WARNING_DURATION = 14 * 60 * 1000; // 14 minutes (1 minute before logout)

export const startInactivityTimer = (onTimeout) => {
  // Clear any existing timers
  clearInactivityTimer();

  // Set a warning timer
  warningTimer = setTimeout(() => {
    // Optional: display a warning to the user (could integrate a modal or toast notification here)
    console.warn('You will be logged out soon due to inactivity.');
  }, WARNING_DURATION);

  // Set the actual timeout timer
  inactivityTimer = setTimeout(() => {
    onTimeout && onTimeout();
  }, TIMEOUT_DURATION);
};

export const clearInactivityTimer = () => {
  if (inactivityTimer) clearTimeout(inactivityTimer);
  if (warningTimer) clearTimeout(warningTimer);
};

// Call this to reset the timer (e.g., on user activity)
export const resetInactivityTimer = (onTimeout) => {
  clearInactivityTimer();
  startInactivityTimer(onTimeout);
};

// Optionally, attach event listeners to track user activity
export const initializeInactivityTracking = (onTimeout) => {
  document.addEventListener('mousemove', () => resetInactivityTimer(onTimeout));
  document.addEventListener('keydown', () => resetInactivityTimer(onTimeout));
  document.addEventListener('click', () => resetInactivityTimer(onTimeout));
  // Start the initial timer
  startInactivityTimer(onTimeout);
};

// Remove listeners if needed
export const removeInactivityTracking = () => {
  document.removeEventListener('mousemove', resetInactivityTimer);
  document.removeEventListener('keydown', resetInactivityTimer);
  document.removeEventListener('click', resetInactivityTimer);
  clearInactivityTimer();
};
