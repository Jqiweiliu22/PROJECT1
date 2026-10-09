# Data sources and image review

Review date: 2026-10-08. This is an initial source audit, not a completed
item-by-item image permission or cultural review.

## Dataset scope

The supplied JSON contains 316 records: 11 from the National Museum of
Australia (NMA) and 305 from the State Library of Western Australia (SLWA).
The retrieval date and screening history in the JSON are supplied claims;
this audit has not independently reconstructed the original extraction.

## NMA

- Official terms: https://www.nma.gov.au/about/our-collection/museum-api/collection-api-terms-of-use
- API text is covered by CC BY-NC 4.0. Images have separate conditions.
- The supplied image labels are Public Domain (5), CC BY-SA 4.0 (4),
  and CC BY-NC-SA 4.0 (2). Individual labels still need source verification.
- Display only images provided through the API, using returned image URLs
  rather than locally hosted copies. Include attribution, image links and
  links back to the institutional content.
- Include: "Collection Explorer was developed using the National Museum
  of Australia's Collection API."
- The terms require a description of the application and free access to
  be emailed to api@nma.gov.au. This has not been done by this audit.

## SLWA

- Dataset: https://catalogue.data.wa.gov.au/en/dataset/digital-photographic-collection
- Collection copyright guidance: https://slwa.wa.gov.au/about/corporate-information/copyright-library-collections
- The JSON labels all 305 images CC BY 4.0. That uniform label is not
  evidence that each photograph has been licensed for reuse.
- 301 SLWA source_url fields still point to the dataset landing page.
  Four now point to individually checked official item pages.
- Review each item's catalogue rights and access conditions. Do not mark
  the SLWA images as cleared merely because the metadata is downloadable.
- Until reviewed, the image permission status is unverified. Page owners
  must avoid presenting these labels as confirmed image permissions.

## Other issues to resolve

- The supplied metadata originally listed raw_count as 642 and
  excluded_count as 235. The original extraction files and filtering
  scripts are not available in this repository, so these figures could
  not be verified and have been removed from the active metadata.
  The current dataset has been counted directly and contains 316 records:
  305 from SLWA and 11 from NMA. No complete extraction or filtering
  history is claimed.
- The description field coverage has been corrected from 153 to 152,
  matching the current records after the second SLWA item correction.
- The dataset-wide licence describes NMA text and cannot represent every
  image and both institutions' material.
- Keyword screening does not establish cultural suitability. Check item
  restrictions and apply appropriate deceased-person notices.
- Source labels must be kept separate from verified rights information.

## Next review tasks

### Second item correction: slwa:b19030149 (2026-10-08)

The official page https://purl.slwa.wa.gov.au/slwa_b1903014_1 identifies
a camel transport camp panorama dated 1908. The user's catalogue screenshot
corroborates the title, date and call number 1935B. The supplied title/date
and description of a 1901 expedition did not match this item. Corrected
title/date, removed the unverified incompatible description, and preserved
the original record in image-review.json. No explicit item-level reuse
licence was found; display URLs are cleared and permission is unverified.
The current dataset retains 316 records and 314 nonempty image URLs.

1. Locate individual SLWA catalogue records and record their source URLs.
2. Record image rights evidence per item, including the reviewed URL and date.
3. Verify the 11 NMA image labels against institutional records/API data.
4. Coordinate with the page owner to display only reviewed images and
   accurate attribution. Core unit tests do not establish image permission.

## First item review: slwa:b18396392

- Initially reviewed by AI on 2026-10-08. On the same date, the team
  member independently opened the official item page and confirmed
  its Terms of use, as reported in the project discussion.
- Title: 219000PD: Centenary parade, 1929.
- Verified item: https://purl.slwa.wa.gov.au/slwa_b1839639_1
- The title, date and call number BA1285 match the supplied record.
- The item's Terms of use require contacting SLWA before publication
  or display beyond personal use. No permission has been obtained.
- The supplied CC BY 4.0 image label therefore cannot be relied on.
- Replaced the generic source_url with the verified item URL, cleared
  image_url and image_large_url, removed the direct-image related link,
  and recorded permission_required. Metadata and the record are retained.
- Original supplied image URL for audit purposes:
  https://slwa.wa.gov.au/images/pd219/219,000PD.jpg
- Updated metadata.image_count to the actual nonempty image URL count
  (315). This is availability information, not a count of cleared images.
- The other 304 SLWA images still need individual review. NMA images
  likewise still need item-level verification.

## Entry 13 source-review summary (2026-10-08)

The current dataset contains 316 records: 305 SLWA and 11 NMA. Two
SLWA items have review entries: slwa:b18396392 requires permission for
publication/display; slwa:b19030149 has unverified image reuse conditions.
Their display URLs remain blank. The other 314 entries are pending review.
314 records contain image URLs, which does not establish display permission.

The five planned Noongar labels and their source/use conditions are recorded
in language-sources.md. Published-source checks have been completed for
those labels, but no language reuse authorization has been recorded.
Remaining item-level permissions, extraction history and public-use
suitability are outstanding; this entry does not claim a completed audit.

## SLWA source matching (2026-10-09)

AI downloaded the official Pictorial collection CSV and matched all 305
SLWA bibliographic record numbers. The 303 records that previously retained
generic source links also matched the snapshot image captions and image URLs
(after normalising HTTP/HTTPS, www and path case). This is snapshot provenance
evidence, not a completed live catalogue or rights review.

Two further item pages were checked in the browser: slwa:b19108564 and
slwa:b19216373. Their displayed headings matched the records and official
snapshot captions; their source_url fields now use those verified pages.
301 generic source links remain. Evidence is in slwa-source-matches.json.
Image URLs and permission statuses have not been changed by this source-link
update; pending image-use reviews remain outstanding.
