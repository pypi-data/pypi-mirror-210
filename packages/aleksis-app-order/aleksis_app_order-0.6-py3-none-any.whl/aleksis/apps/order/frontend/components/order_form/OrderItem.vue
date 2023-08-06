<template>
  <v-row>
    <v-col cols="12" sm="4" md="3" lg="3" xl="3">
      <v-img
        v-if="item.image"
        :src="item.image"
        :alt="item.name"
        aspect-ratio="1"
        class="order-item-image mb-2"
      ></v-img>
      <div
        v-if="!item.image"
        class="grey lighten-3 order-item-fake-image mb-2 align-center justify-center d-none d-sm-flex"
      >
        <v-icon size="80"> mdi-package-variant-closed </v-icon>
      </div>
    </v-col>

    <v-col cols="12" sm="8" md="9" lg="9" xl="9">
      <div class="text-subtitle-1 font-weight-medium black--text mb-2">
        {{ item.name }}
      </div>
      <slot name="right">
        <div
          v-html="item.notice"
          class="text-body-2 text--secondary item-description mb-3"
        />
        <v-row>
          <v-col>
            <div class="text-caption">{{ $t("order.items.price") }}</div>
            <div class="text-h6 font-weight-medium">
              {{ priceWithCurrency }}
            </div>
          </v-col>
          <v-col>
            <div class="text-caption">{{ $t("order.items.quantity") }}</div>
            <div v-if="!readOnly">
              <v-autocomplete
                v-model="count"
                auto-select-first
                outlined
                dense
                :items="countItems"
              />
            </div>
            <div v-if="readOnly" class="text-h6 font-weight-medium">
              {{ count }}
            </div>
          </v-col>
          <v-col>
            <div class="text-caption text-right">
              {{ $t("order.items.total") }}
            </div>
            <div class="text-h6 font-weight-medium text-right">
              {{ totalWithCurrency }}
            </div>
          </v-col>
        </v-row>
      </slot>
    </v-col>
  </v-row>
</template>

<script>
import { formatCurrency } from "./util";

export default {
  name: "OrderItem",
  data() {
    return {
      count: this.item.count,
    };
  },
  computed: {
    countItems() {
      let items = [];
      for (let i = 0; i <= this.item.maxCount; i++) {
        items.push(i);
      }
      return items;
    },
    priceWithCurrency() {
      return formatCurrency(this.item.price);
    },
    totalWithCurrency() {
      return formatCurrency(this.item.total);
    },
  },
  watch: {
    item() {
      this.count = this.item.count || 0;
    },
    count(val) {
      this.$emit("update-count", this.item, val);
    },
  },
  props: {
    item: {
      type: Object,
      required: true,
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
