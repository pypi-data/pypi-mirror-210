<template>
  <div>
    <v-radio :value="option.id" :disabled="disabled" class="mb-2">
      <template #label>
        <v-row no-gutters class="mt-1">
          <v-col cols="10">
            <div class="text-subtitle-1 font-weight-medium black--text">
              {{ option.name }}
            </div>
          </v-col>
          <v-col
            cols="2"
            class="text-right text-h6 font-weight-medium black--text"
          >
            {{ priceWithCurrency }}
          </v-col>
        </v-row>
      </template>
    </v-radio>
    <div
      v-html="option.notice"
      class="text-body-2 text--secondary item-description mb-3"
    />
  </div>
</template>

<script>
import { formatCurrency } from "./util";

export default {
  name: "OptionRadio",
  computed: {
    priceWithCurrency() {
      return this.option.price
        ? formatCurrency(this.option.price)
        : this.$t("order.free");
    },
  },
  props: {
    option: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
