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
- All 305 source_url fields currently point to the dataset landing page,
  rather than providing individual catalogue sources.
- Review each item's catalogue rights and access conditions. Do not mark
  the SLWA images as cleared merely because the metadata is downloadable.
- Until reviewed, the image permission status is unverified. Page owners
  must avoid presenting these labels as confirmed image permissions.

## Other issues to resolve

- raw_count (642), excluded_count (235) and record_count (316) do not
  reconcile as a simple subtraction. Explain extraction/merging stages
  from actual evidence instead of inventing a cleaning history.
- The dataset-wide licence describes NMA text and cannot represent every
  image and both institutions' material.
- Keyword screening does not establish cultural suitability. Check item
  restrictions and apply appropriate deceased-person notices.
- Source labels must be kept separate from verified rights information.

## Next review tasks

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
