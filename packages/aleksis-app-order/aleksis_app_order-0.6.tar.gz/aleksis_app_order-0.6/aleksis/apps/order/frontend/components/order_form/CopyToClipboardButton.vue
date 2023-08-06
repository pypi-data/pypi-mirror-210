<template>
  <v-tooltip top v-model="copied">
    <template #activator="{ on, attrs }">
      <v-btn
        icon
        color="primary"
        @click="copyToClipboard(text)"
        v-bind="$attrs"
      >
        <v-icon>mdi-content-copy</v-icon>
      </v-btn>
    </template>
    <span>{{ $t("order.copied") }}</span>
  </v-tooltip>
</template>

<script>
export default {
  name: "CopyToClipboardButton",
  data() {
    return {
      copied: false,
    };
  },
  props: {
    text: {
      type: String,
      required: true,
    },
  },
  methods: {
    copyToClipboard(text) {
      navigator.clipboard.writeText(text);
      this.copied = true;
      setTimeout(() => {
        this.copied = false;
      }, 1000);
    },
  },
};
</script>
