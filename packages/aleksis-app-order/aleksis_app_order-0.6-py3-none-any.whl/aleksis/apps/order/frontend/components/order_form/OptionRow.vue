<template>
  <v-row>
    <v-col
      cols="9"
      md="10"
      lg="10"
      xl="10"
      class="text-body-1 font-weight-medium"
    >
      {{ option.name }}
    </v-col>
    <v-col cols="3" md="2" lg="2" xl="2" class="d-flex justify-end">
      <div class="text-right text-body-1 font-weight-medium">
        {{ priceWithCurrency }}
      </div>
    </v-col>
  </v-row>
</template>

<script>
import { formatCurrency } from "./util";

export default {
  name: "OptionRow",
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
  },
};
</script>
