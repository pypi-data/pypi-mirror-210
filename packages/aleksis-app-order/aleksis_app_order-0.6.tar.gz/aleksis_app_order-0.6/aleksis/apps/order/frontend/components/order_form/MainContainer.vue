<template>
  <v-row>
    <v-col>
      <div class="order-main-container">
        <slot></slot>
      </div>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: "MainContainer",
};
</script>

<style scoped>
.order-main-container {
  max-width: 1000px;
  margin: 0 auto;
}
</style>
