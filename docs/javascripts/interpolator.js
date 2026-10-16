(function () {
  function buildInterpolator() {
    if (document.getElementById('awp-interp-button')) return;

    // ---- Floating button ----
    var btn = document.createElement('button');
    btn.id = 'awp-interp-button';
    btn.type = 'button';
    btn.textContent = 'Interpolator';
    document.body.appendChild(btn);

    // ---- Dropdown panel ----
    var panel = document.createElement('div');
    panel.id = 'awp-interp-panel';
    panel.style.display = 'none';
    panel.innerHTML = [
      '<div class="awp-interp-header">',
      '  <span>Linear Interpolator</span>',
      '  <button type="button" id="awp-interp-close" aria-label="Close">&times;</button>',
      '</div>',
      '<p class="awp-interp-instructions">Fill in five values and leave one blank, then click Calculate.</p>',
      '<div class="awp-interp-grid">',
      '  <div class="awp-interp-col-label">X</div>',
      '  <div class="awp-interp-col-label">Y</div>',
      '  <input type="text" class="awp-interp-input" data-row="0" data-col="x">',
      '  <input type="text" class="awp-interp-input" data-row="0" data-col="y">',
      '  <input type="text" class="awp-interp-input" data-row="1" data-col="x">',
      '  <input type="text" class="awp-interp-input" data-row="1" data-col="y">',
      '  <input type="text" class="awp-interp-input" data-row="2" data-col="x">',
      '  <input type="text" class="awp-interp-input" data-row="2" data-col="y">',
      '</div>',
      '<div class="awp-interp-actions">',
      '  <button type="button" id="awp-interp-calc">Calculate</button>',
      '  <button type="button" id="awp-interp-clear">Clear</button>',
      '</div>',
      '<div id="awp-interp-error" class="awp-interp-error"></div>'
    ].join('');
    document.body.appendChild(panel);

    // Toggle open/closed
    btn.addEventListener('click', function () {
      panel.style.display = (panel.style.display === 'none') ? 'block' : 'none';
    });
    panel.querySelector('#awp-interp-close').addEventListener('click', function () {
      panel.style.display = 'none';
    });
    panel.querySelector('#awp-interp-clear').addEventListener('click', function () {
      panel.querySelectorAll('.awp-interp-input').forEach(function (i) { i.value = ''; });
      panel.querySelector('#awp-interp-error').textContent = '';
    });

    // The actual math
    panel.querySelector('#awp-interp-calc').addEventListener('click', function () {
      var errorBox = panel.querySelector('#awp-interp-error');
      errorBox.textContent = '';

      var rows = [0, 1, 2].map(function (r) {
        var xInput = panel.querySelector('.awp-interp-input[data-row="' + r + '"][data-col="x"]');
        var yInput = panel.querySelector('.awp-interp-input[data-row="' + r + '"][data-col="y"]');
        return { xInput: xInput, yInput: yInput, x: xInput.value.trim(), y: yInput.value.trim() };
      });

      var blanks = [];
      rows.forEach(function (row, i) {
        if (row.x === '') blanks.push({ row: i, col: 'x' });
        if (row.y === '') blanks.push({ row: i, col: 'y' });
      });

      if (blanks.length !== 1) {
        errorBox.textContent = 'Please fill in exactly five values and leave exactly one blank.';
        return;
      }

      var blank = blanks[0];
      var known = rows.filter(function (_, i) { return i !== blank.row; });

      var x1 = parseFloat(known[0].x), y1 = parseFloat(known[0].y);
      var x2 = parseFloat(known[1].x), y2 = parseFloat(known[1].y);

      if ([x1, y1, x2, y2].some(isNaN)) {
        errorBox.textContent = 'The two fully-completed rows must contain valid numbers.';
        return;
      }
      if (x1 === x2) {
        errorBox.textContent = 'The two known rows must have different X values.';
        return;
      }

      var slope = (y2 - y1) / (x2 - x1);
      var targetRow = rows[blank.row];

      if (blank.col === 'y') {
        var xKnown = parseFloat(targetRow.x);
        if (isNaN(xKnown)) {
          errorBox.textContent = 'Please enter a valid X value in the incomplete row.';
          return;
        }
        targetRow.yInput.value = round(y1 + slope * (xKnown - x1));
      } else {
        var yKnown = parseFloat(targetRow.y);
        if (isNaN(yKnown)) {
          errorBox.textContent = 'Please enter a valid Y value in the incomplete row.';
          return;
        }
        if (slope === 0) {
          errorBox.textContent = 'Cannot solve for X: the two known points have equal Y values.';
          return;
        }
        targetRow.xInput.value = round(x1 + (yKnown - y1) / slope);
      }
    });

    function round(n) {
      return Math.round(n * 1e6) / 1e6;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildInterpolator);
  } else {
    buildInterpolator();
  }
})();