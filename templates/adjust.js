function setCardHeight() {
	// カードの高さを揃える
	const cards = document.querySelectorAll(".card");
	let maxHeight = 0;
	cards.forEach((card) => {
		const height = card.offsetHeight;
		if (height > maxHeight) {
		maxHeight = height;
		}
	});
	cards.forEach((card) => {
		card.style.height = `${maxHeight}px`;
	});
}
setCardHeight();
//detailsタグの展開と高さの調整を制御する
jQuery(document).ready(function() {
	jQuery('details').each(function() {
		var $details = jQuery(this);
		var $summary = $details.children('summary');
		var $content = $details.children(':not(summary)');
		$summary.addClass('accordion-header');
		$summary.attr('data-toggle', 'collapse');
		$summary.attr('data-target', '#' + $details.attr('id') + '-content');
		$summary.wrapInner('<button class="accordion-button" type="button"></button>');
		$content.addClass('accordion-collapse collapse');
		$content.attr('id', $details.attr('id') + '-content');
		$content.attr('data-parent', '#' + $details.attr('id'));
		if ($details.attr('open') !== undefined) {
		$content.addClass('show');
		}
	});
	jQuery('.accordion-button').click(function() {
		var $content = jQuery(jQuery(this).attr('data-target'));
		var isOpen = $content.hasClass('show');
		$content.hide(isOpen ? 'hide' : 'show');
	});
});
// ページを読み込んだ時に注意事項のリストを閉じる
document.addEventListener("DOMContentLoaded", function() {
	const accordionButton = document.querySelector('.accordion-button');
	const accordionCollapse = document.querySelector('.accordion-collapse');
	accordionButton.classList.add('collapsed');
	accordionCollapse.classList.remove('show');
});