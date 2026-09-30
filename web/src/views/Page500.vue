<template>
  <div class="error-page">
    <h1 class="error-code">500</h1>
    <div>
      <h4>Houston, we have a problem!</h4>
      <p class="muted">The page you are looking for is temporarily unavailable.</p>
    </div>
  </div>
</template>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  min-height: 100vh;
  padding: 1rem;
}

.error-code {
  margin: 0;
  font-size: 4.5rem;
  font-weight: 300;
}

.error-page p {
  margin: 0;
}
</style>
