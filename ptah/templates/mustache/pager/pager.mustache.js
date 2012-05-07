function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, stack2, foundHelper, tmp1, self=this, functionType="function", helperMissing=helpers.helperMissing, undef=void 0, escapeExpression=this.escapeExpression, blockHelperMissing=helpers.blockHelperMissing;

function program1(depth0,data) {

  var buffer = "", stack1;
  buffer += "\n    <li class=\"prev\">\n      <a href=\"javascript: void(0)\"\n        data-action=\"page\" data-page=\"";
  foundHelper = helpers.prev;
  stack1 = foundHelper || depth0.prev;
  if(typeof stack1 === functionType) { stack1 = stack1.call(depth0, { hash: {} }); }
  else if(stack1=== undef) { stack1 = helperMissing.call(depth0, "prev", { hash: {} }); }
  buffer += escapeExpression(stack1) + "\">&larr; Previous</a>\n    </li>\n    ";
  return buffer;}

function program3(depth0,data) {


  return "\n    <li class=\"prev disabled\">\n      <a href=\"javascript:void(0)\">&larr; Previous</a>\n    </li>\n    ";}

function program5(depth0,data) {

  var buffer = "", stack1, stack2;
  buffer += "\n      ";
  foundHelper = helpers.no;
  stack1 = foundHelper || depth0.no;
  stack2 = helpers['if'];
  tmp1 = self.program(6, program6, data);
  tmp1.hash = {};
  tmp1.fn = tmp1;
  tmp1.inverse = self.program(8, program8, data);
  stack1 = stack2.call(depth0, stack1, tmp1);
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n    ";
  return buffer;}
function program6(depth0,data) {

  var buffer = "", stack1;
  buffer += "\n      <li class=\"";
  foundHelper = helpers.cls;
  stack1 = foundHelper || depth0.cls;
  if(typeof stack1 === functionType) { stack1 = stack1.call(depth0, { hash: {} }); }
  else if(stack1=== undef) { stack1 = helperMissing.call(depth0, "cls", { hash: {} }); }
  buffer += escapeExpression(stack1) + "\">\n        <a href=\"javascript:void(0)\"\n          data-action=\"page\" data-page=\"";
  foundHelper = helpers.no;
  stack1 = foundHelper || depth0.no;
  if(typeof stack1 === functionType) { stack1 = stack1.call(depth0, { hash: {} }); }
  else if(stack1=== undef) { stack1 = helperMissing.call(depth0, "no", { hash: {} }); }
  buffer += escapeExpression(stack1) + "\">";
  foundHelper = helpers.no;
  stack1 = foundHelper || depth0.no;
  if(typeof stack1 === functionType) { stack1 = stack1.call(depth0, { hash: {} }); }
  else if(stack1=== undef) { stack1 = helperMissing.call(depth0, "no", { hash: {} }); }
  buffer += escapeExpression(stack1) + "</a>\n      </li>\n      ";
  return buffer;}

function program8(depth0,data) {


  return "\n      <li class=\"disabled\">\n        <a href=\"javascript: void(0)\">...</a>\n      </li>\n      ";}

function program10(depth0,data) {

  var buffer = "", stack1;
  buffer += "\n    <li class=\"next\">\n      <a href=\"javascript:void(0)\"\n        data-action=\"page\" data-page=\"";
  foundHelper = helpers.next;
  stack1 = foundHelper || depth0.next;
  if(typeof stack1 === functionType) { stack1 = stack1.call(depth0, { hash: {} }); }
  else if(stack1=== undef) { stack1 = helperMissing.call(depth0, "next", { hash: {} }); }
  buffer += escapeExpression(stack1) + "\">Next &rarr;</a>\n    </li>\n    ";
  return buffer;}

function program12(depth0,data) {


  return "\n    <li class=\"next disabled\">\n      <a href=\"javascript: void(0)\">Next &rarr;</a>\n    </li>\n    ";}

  buffer += "<div class=\"pagination\">\n  <ul>\n    ";
  foundHelper = helpers.prev;
  stack1 = foundHelper || depth0.prev;
  stack2 = helpers['if'];
  tmp1 = self.program(1, program1, data);
  tmp1.hash = {};
  tmp1.fn = tmp1;
  tmp1.inverse = self.program(3, program3, data);
  stack1 = stack2.call(depth0, stack1, tmp1);
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n    ";
  foundHelper = helpers.pages;
  stack1 = foundHelper || depth0.pages;
  tmp1 = self.program(5, program5, data);
  tmp1.hash = {};
  tmp1.fn = tmp1;
  tmp1.inverse = self.noop;
  if(foundHelper && typeof stack1 === functionType) { stack1 = stack1.call(depth0, tmp1); }
  else { stack1 = blockHelperMissing.call(depth0, stack1, tmp1); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n    ";
  foundHelper = helpers.next;
  stack1 = foundHelper || depth0.next;
  stack2 = helpers['if'];
  tmp1 = self.program(10, program10, data);
  tmp1.hash = {};
  tmp1.fn = tmp1;
  tmp1.inverse = self.program(12, program12, data);
  stack1 = stack2.call(depth0, stack1, tmp1);
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n  </ul>\n</div>\n";
  return buffer;}

