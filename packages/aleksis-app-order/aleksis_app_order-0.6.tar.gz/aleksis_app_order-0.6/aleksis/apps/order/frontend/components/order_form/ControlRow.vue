<template>
  <div class="d-flex">
    <v-btn
      v-if="step > 1"
      color="primary"
      text
      @click="$emit('set-step', step - 1)"
    >
      <v-icon left>mdi-chevron-left</v-icon>
      {{ $t("order.actions.back") }}
    </v-btn>
    <v-spacer />
    <v-btn
      v-if="finalStep"
      color="primary"
      :disabled="nextDisabled || nextLoading"
      :loading="nextLoading"
      @click="$emit('confirm')"
    >
      {{ $t("order.actions.confirm") }}
      <v-icon right>mdi-send-outline</v-icon>
    </v-btn>
    <v-btn
      v-else
      color="primary"
      :disabled="nextDisabled || nextLoading"
      :loading="nextLoading"
      @click="$emit('set-step', step + 1)"
    >
      {{ $t("order.actions.next") }}
      <v-icon right>mdi-chevron-right</v-icon>
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "ControlRow",
  props: {
    step: {
      type: Number,
      required: true,
    },
    nextDisabled: {
      type: Boolean,
      default: false,
    },
    finalStep: {
      type: Boolean,
      default: false,
    },
    nextLoading: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
